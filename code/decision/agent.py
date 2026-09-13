from code.models import Request, UserProfile, OutputRecommendation
from code.forecasting.cash_flow import CashFlowSimulator
from code.decision.strategies import StrategyGenerator
from code.decision.explanations import ExplanationGenerator
from code.ml.risk_model import StatisticalRiskModel
from code.validation.validator import DeterministicValidator

class DecisionAgent:
    def __init__(self, data_loader, media_extractor, currency_converter):
        self.data_loader = data_loader
        self.media_extractor = media_extractor
        self.currency_converter = currency_converter
        
        self.users = data_loader.load_users()
        self.events = data_loader.load_events()
        self.options = data_loader.load_payment_options()
        self.requests = data_loader.load_requests()
        
        self.risk_model = StatisticalRiskModel()
        self.explanation_gen = ExplanationGenerator()
        self.validator = DeterministicValidator()
        
    def process_request(self, request: Request, demo: bool = False) -> OutputRecommendation:
        user = self.users.get(request.user_id)
        events = self.events.get(request.user_id, [])
        options = self.options.get(request.request_id, [])
        messages = self.media_extractor.get_messages_for_user(request.user_id)
        
        # 1. Normalize currency
        try:
            request.normalized_requested_amount = self.currency_converter.convert(
                request.requested_amount, "EUR", user.home_currency, request.request_date
            ) # wait, request is already in home currency according to rules?
            # "Balances, requests, payment options, and output amounts use the user's home_currency."
            request.normalized_requested_amount = request.requested_amount
        except Exception as e:
            request.normalized_requested_amount = request.requested_amount
            
        for ev in events:
            # Extract missing amounts from images
            if ev.amount is None:
                amt = self.media_extractor.get_amount_from_event(ev.event_id)
                ev.amount = amt if amt is not None else 0.0 # fallback
                
            try:
                ev.normalized_amount = self.currency_converter.convert(
                    ev.amount, ev.currency, user.home_currency, ev.settlement_date
                )
            except:
                ev.normalized_amount = ev.amount
                
        for opt in options:
            opt.normalized_payment_amount = opt.payment_amount
            opt.normalized_total_payable_amount = opt.total_payable_amount
            
        # 2. Setup Simulator
        simulator = CashFlowSimulator(user, events, messages)
        generator = StrategyGenerator(simulator)
        
        if demo:
            print(f"\n--- DEMO MODE for {request.request_id} ---")
            print(f"User Balance: {user.current_available_balance}, Min required: {user.minimum_balance_to_keep}")
            
        # 3. Generate Strategies
        strategies = generator.generate_strategies(request, options)
        
        # Filter based on user preferences
        valid_methods = set(user.payment_methods_user_will_consider)
        
        best_strategy = None
        best_score = -float('inf')
        best_min_bal = 0.0
        
        for s in strategies:
            # check preference
            if s['method'] not in valid_methods and s['method'] != 'wait':
                continue
                
            # simulate to get min balance for scoring
            payments = []
            if s['plan'] != 'none':
                for p in s['plan'].split('|'):
                    d, a = p.split(':')
                    import datetime
                    payments.append({'date': datetime.date.fromisoformat(d), 'amount': float(a)})
                    
            res = simulator.simulate(request.request_date, 90, payments)
            score = self.risk_model.score_strategy(s, user, res['min_balance'])
            
            if demo:
                print(f"Strategy {s['method']}: Score={score:.2f}, MinBal={res['min_balance']:.2f}")
                
            if score > best_score:
                best_score = score
                best_strategy = s
                best_min_bal = res['min_balance']
                
        if not best_strategy:
            best_strategy = {
                'method': 'not_recommended',
                'status': 'not_affordable',
                'plan': 'none',
                'amount_safe': 0.0,
                'earliest_date': '',
                'changes': 'none'
            }
            
        expl = self.explanation_gen.generate(best_strategy, request, user, best_min_bal)
        
        earliest_date_str = best_strategy['earliest_date'].isoformat() if best_strategy.get('earliest_date') else ""
        
        rec = OutputRecommendation(
            request_id=request.request_id,
            amount_safe_to_pay=best_strategy.get('amount_safe', 0.0),
            affordability_status=best_strategy['status'],
            recommended_payment_method=best_strategy['method'],
            payment_plan=best_strategy['plan'],
            earliest_date_for_full_payment=earliest_date_str,
            spending_changes_needed=best_strategy['changes'],
            decision_explanation=expl
        )
        
        # 4. Validate
        if not self.validator.validate(rec, request):
            if demo: print("Validation failed for best strategy! Falling back.")
            rec = OutputRecommendation(request_id=request.request_id)
            
        return rec
