from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

@dataclass
class UserProfile:
    user_id: str
    home_currency: str
    current_available_balance: float
    minimum_balance_to_keep: float
    financial_priorities: List[str]
    expense_categories_to_protect: List[str]
    expense_categories_user_is_willing_to_reduce: List[str]
    expense_categories_user_is_willing_to_stop: List[str]
    payment_methods_user_will_consider: List[str]
    max_installment_months: Optional[int]

@dataclass
class FinancialEvent:
    event_id: str
    user_id: str
    event_type: str
    description: str
    category: str
    direction: str
    amount: Optional[float]
    currency: str
    event_date: date
    settlement_date: date
    status: str
    linked_event_id: Optional[str]
    flexibility: str
    minimum_allowed_amount: Optional[float]
    is_recurring: bool = False
    
    # Internal usage
    normalized_amount: Optional[float] = None # in home currency

@dataclass
class Request:
    request_id: str
    user_id: str
    request_date: date
    request_type: str
    requested_amount: float
    desired_completion_date: date
    allows_partial_payment: bool
    request_text: str

    # Joined
    normalized_requested_amount: float = 0.0

@dataclass
class PaymentOption:
    payment_option_id: str
    request_id: str
    payment_method: str
    payment_amount: float
    number_of_payments: int
    first_payment_date: date
    payment_frequency_days: int
    financing_fee: float
    total_payable_amount: float
    
    # normalized
    normalized_payment_amount: float = 0.0
    normalized_total_payable_amount: float = 0.0

@dataclass
class OutputRecommendation:
    request_id: str
    amount_safe_to_pay: float = 0.0
    affordability_status: str = "not_affordable"
    recommended_payment_method: str = "not_recommended"
    payment_plan: str = "none"
    earliest_date_for_full_payment: str = ""
    spending_changes_needed: str = "none"
    decision_explanation: str = ""

