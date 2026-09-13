class ExplanationGenerator:
    def generate(self, strategy: dict, request: 'Request', user: 'UserProfile', min_balance: float) -> str:
        method = strategy.get('method')
        currency = user.home_currency
        
        if method == 'full_payment':
            return f"Pay {currency} {strategy['amount_safe']:.2f} today. This keeps the {currency} {user.minimum_balance_to_keep:.2f} minimum protected, with a lowest projected balance of {currency} {min_balance:.2f}."
        elif method == 'wait':
            return f"Wait until {strategy['earliest_date'].strftime('%d %B %Y')}, then pay {currency} {strategy['plan'].split(':')[1]} in full. Paying sooner would put the {currency} {user.minimum_balance_to_keep:.2f} minimum at risk."
        elif method == 'installments':
            parts = strategy['plan'].split('|')
            count = len(parts)
            amt = parts[0].split(':')[1]
            date_str = strategy['earliest_date'].strftime('%d %B %Y') if strategy.get('earliest_date') else "today" # approximations
            return f"Use {count} installments of {currency} {amt}, starting {date_str}. This leaves at least {currency} {min_balance:.2f} available."
        elif method == 'partial_payment':
            return f"Pay {currency} {strategy['amount_safe']:.2f} today, and the rest later. This protects the {currency} {user.minimum_balance_to_keep:.2f} minimum."
        else:
            return f"Do not make this payment. None of the available options keeps the {currency} {user.minimum_balance_to_keep:.2f} minimum protected."
