from datetime import date, timedelta
from typing import List, Dict, Optional
from copy import deepcopy

from code.models import Request, PaymentOption, UserProfile
from code.forecasting.cash_flow import CashFlowSimulator

class StrategyGenerator:
    def __init__(self, simulator: CashFlowSimulator):
        self.simulator = simulator

    def generate_strategies(self, request: Request, options: List[PaymentOption]) -> List[Dict]:
        strategies = []
        
        # We need to find amount_safe_to_pay and earliest_date_for_full_payment
        amount_safe = self._find_amount_safe(request)
        earliest_date = self._find_earliest_date(request)
        
        # Full payment strategy
        if amount_safe == request.normalized_requested_amount:
            strategies.append({
                'method': 'full_payment',
                'status': 'affordable_now',
                'plan': f"{request.request_date.isoformat()}:{request.normalized_requested_amount:.2f}",
                'amount_safe': amount_safe,
                'earliest_date': request.request_date,
                'changes': 'none',
                'score': 100
            })
            
        # Wait strategy
        if earliest_date and earliest_date > request.request_date and earliest_date <= request.desired_completion_date:
            strategies.append({
                'method': 'wait',
                'status': 'affordable_later',
                'plan': f"{earliest_date.isoformat()}:{request.normalized_requested_amount:.2f}",
                'amount_safe': amount_safe,
                'earliest_date': earliest_date,
                'changes': 'none',
                'score': 80
            })
            
        # Partial payment strategy
        if request.allows_partial_payment and 0 < amount_safe < request.normalized_requested_amount:
            if earliest_date and earliest_date <= request.desired_completion_date:
                rem = request.normalized_requested_amount - amount_safe
                plan = f"{request.request_date.isoformat()}:{amount_safe:.2f}|{earliest_date.isoformat()}:{rem:.2f}"
                strategies.append({
                    'method': 'partial_payment',
                    'status': 'affordable_with_plan',
                    'plan': plan,
                    'amount_safe': amount_safe,
                    'earliest_date': earliest_date,
                    'changes': 'none',
                    'score': 90
                })
                
        # Installments
        for opt in options:
            if opt.payment_method == 'installments':
                # Generate plan string
                d = opt.first_payment_date
                plan_parts = []
                for i in range(opt.number_of_payments):
                    plan_parts.append(f"{d.isoformat()}:{opt.normalized_payment_amount:.2f}")
                    d += timedelta(days=opt.payment_frequency_days)
                plan = "|".join(plan_parts)
                
                # Check if safe
                payments = [{'date': opt.first_payment_date + timedelta(days=i*opt.payment_frequency_days), 'amount': opt.normalized_payment_amount} for i in range(opt.number_of_payments)]
                res = self.simulator.simulate(request.request_date, 90, payments)
                
                if res['is_safe']:
                    strategies.append({
                        'method': 'installments',
                        'status': 'affordable_with_plan',
                        'plan': plan,
                        'amount_safe': amount_safe,
                        'earliest_date': earliest_date, # earliest date independently calculated
                        'changes': 'none',
                        'score': 85,
                        'payment_option_id': opt.payment_option_id
                    })
                    
        return strategies
        
    def _find_amount_safe(self, request: Request) -> float:
        # Binary search or simple loop to find max safe amount today
        low = 0.0
        high = request.normalized_requested_amount
        best = 0.0
        
        for _ in range(10): # 10 iterations of binary search
            mid = (low + high) / 2
            res = self.simulator.simulate(request.request_date, 90, [{'date': request.request_date, 'amount': mid}])
            if res['is_safe']:
                best = mid
                low = mid
            else:
                high = mid
                
        # To avoid floating point issues, let's round
        return round(best, 2)
        
    def _find_earliest_date(self, request: Request) -> Optional[date]:
        # Search over the next 90 days for a date where paying full amount is safe
        for i in range(90):
            test_date = request.request_date + timedelta(days=i)
            res = self.simulator.simulate(request.request_date, 90, [{'date': test_date, 'amount': request.normalized_requested_amount}])
            if res['is_safe']:
                return test_date
        return None
