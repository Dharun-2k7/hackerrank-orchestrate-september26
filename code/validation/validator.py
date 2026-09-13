import re
from typing import Dict, List, Optional
from code.models import OutputRecommendation, Request

class DeterministicValidator:
    def __init__(self):
        pass

    def validate(self, recommendation: OutputRecommendation, request: Request) -> bool:
        # Check basic constraints
        if not (0 <= recommendation.amount_safe_to_pay <= request.normalized_requested_amount + 0.01):
            print(f"Validation failed: amount_safe_to_pay {recommendation.amount_safe_to_pay} out of bounds for {request.request_id}")
            return False
            
        # Check status and method logic
        valid_statuses = ['affordable_now', 'affordable_with_plan', 'affordable_later', 'not_affordable']
        valid_methods = ['full_payment', 'partial_payment', 'installments', 'wait', 'not_recommended']
        
        if recommendation.affordability_status not in valid_statuses:
            return False
        if recommendation.recommended_payment_method not in valid_methods:
            return False
            
        if recommendation.affordability_status == 'not_affordable':
            if recommendation.recommended_payment_method != 'not_recommended':
                return False
                
        # Check plan structure
        if recommendation.payment_plan != 'none':
            payments = recommendation.payment_plan.split('|')
            total = 0
            for p in payments:
                if ':' not in p:
                    return False
                date_str, amt_str = p.split(':')
                try:
                    total += float(amt_str)
                except ValueError:
                    return False
            
            if recommendation.recommended_payment_method == 'partial_payment':
                if len(payments) != 2:
                    return False
                # Verify sums (within small float tolerance)
                if abs(total - request.normalized_requested_amount) > 1.0:
                    return False
                    
        return True
