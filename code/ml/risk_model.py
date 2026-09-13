from models import UserProfile

class StatisticalRiskModel:
    def __init__(self):
        pass

    def score_strategy(self, strategy: dict, user: 'UserProfile', min_balance: float) -> float:
        # Transparent scoring heuristic
        # Start with base score from generator
        score = strategy.get('score', 50)
        
        # Buffer margin (safety)
        buffer = min_balance - user.minimum_balance_to_keep
        if buffer > user.minimum_balance_to_keep:
            score += 20
        elif buffer < 0:
            return -float('inf') # unsafe
            
        # Completion speed
        if strategy['method'] == 'full_payment':
            score += 15
        elif strategy['method'] == 'wait':
            score -= 10
            
        # Simplicity (fewer payments)
        if strategy['method'] == 'installments':
            score -= 5
            
        return score
