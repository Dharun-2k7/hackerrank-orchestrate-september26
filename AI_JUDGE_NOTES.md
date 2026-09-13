# AI Judge Notes

### Why is this an agent rather than a classifier?
This system uses a dynamic decision-making process involving information retrieval (from events and messages), structured reasoning (cash-flow forecasting), candidate strategy generation, constraint validation, and multi-factor scoring. It reasons about future consequences rather than simply mapping inputs to outputs statically.

### Why do you forecast day-by-day?
A static balance check is insufficient because upcoming scheduled expenses or pending transactions can pull the balance below the safe minimum on a specific future day. Day-by-day simulation guarantees the minimum balance is maintained at all points.

### Why are rules used for safety?
Rules enforce hard financial constraints (like minimum balance and essential expenses) deterministically. This guarantees the user's financial safety, which statistical models alone cannot guarantee due to their probabilistic nature.

### Why is ML not allowed to override constraints?
ML is used for risk estimation and strategy ranking. If ML could override a hard constraint, it might recommend an unsafe transaction simply because it shares features with historically safe transactions, putting the user in financial distress.

### How are images used?
Images provide supplementary evidence, specifically the amounts for transactions where the value is missing from the structured data. They are linked via `related_event_id` and parsed using OCR/heuristics to recover the missing financial facts.

### How are messages used?
Messages provide unstructured context regarding changes in salary, upcoming commitments, or flexibility of expenses. We use deterministic pattern matching to extract confirmed income amounts and dates, and use them to adjust the cash flow forecast.

### How do you prevent double-counting?
We explicitly link recurring events and check event status. Pending one-time events are counted if they will settle during the forecast period, while unrealized or duplicate occurrences are filtered out.

### How do you handle missing amounts?
Missing amounts are cross-referenced with `images.csv` to find the associated PNG file, from which the amount is extracted using OCR/text-extraction logic. If unrecoverable, we fall back safely.

### How do you handle recurring events?
Recurring events are simulated forward month-by-month through the 90-day forecast horizon. If a message amends a recurring income amount, the projection uses the updated amount from the effective date onwards.

### How do you handle currency conversion?
All amounts are normalized to the user's `home_currency` using the provided `exchange_rates.csv`. We look up the latest available rate on or immediately prior to the event's settlement date or request date.

### How do you personalize recommendations?
The system tailors decisions using each user's unique `minimum_balance_to_keep`, financial priorities, preferred payment methods, and willingness to reduce/stop specific flexible expenses.

### How do you choose between payment strategies?
Feasible strategies are generated and filtered through hard constraints. The remaining safe strategies are scored using a transparent statistical model prioritizing safety (buffer margin), speed of completion, and simplicity. 

### Why did you choose your ML model?
We chose a transparent statistical risk-scoring heuristic instead of a black-box supervised model because there were only 25 labeled examples, making complex models highly prone to overfitting and poor generalization on unseen test data.

### How did you prevent overfitting?
By prioritizing deterministic financial rules for safety and using generalized heuristics (like expense-to-income ratio and buffer margin) for ranking, we avoid memorizing the small sample set.

### How did you evaluate the system?
The system was evaluated against the 25 ground-truth labels in `sample_requests.csv` using `evaluate.py`, computing metrics like status accuracy, method accuracy, and MAE for `amount_safe_to_pay`, while ensuring zero constraint violations.

### What happens when the ML model disagrees with the rules?
The rules always win. If the risk model favors an option but the cash-flow simulator flags it as violating a hard constraint (e.g., dropping below the minimum balance), the option is disqualified before final selection.

### How did you ensure deterministic behavior?
We avoided non-deterministic LLM generations in the core logic path. Currency lookup, forecasting, and strategy scoring rely on fixed, repeatable mathematical rules.

### How did you ensure installment plans are valid?
The strategy generator only considers installment plans exactly as provided in `request_payment_options.csv`, using their specified dates, amounts, frequencies, and fees.

### How did you prevent modifying essential expenses?
Spending changes only target events whose categories are explicitly listed in the user's `expense_categories_user_is_willing_to_reduce` or `stop`. Categories in `expense_categories_to_protect` are strictly protected.

### What are the system's limitations?
1. The 90-day forecast assumes future months follow similar basic structures, which may miss irregular annual expenses not explicitly scheduled.
2. The simple message extraction heuristics might miss complex natural language nuances without a sophisticated NLP engine.
