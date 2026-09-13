# Buy or Wait? AI Financial Agent

## 1. Problem
The "Buy or Wait" challenge requires building an AI agent that decides whether a user can safely afford a requested expense. It considers the user's current balance, recurring expenses, pending payments, payment options, and information embedded in messages/images.

## 2. Architecture
The architecture is modular:
- **Observe & Understand**: Ingest CSV data, normalize currencies, and extract confirmed amounts from messages and images.
- **Forecast**: Perform a day-by-day cash flow simulation across 90 days.
- **Generate**: Create candidate strategies (full payment, installments, partial, wait).
- **Assess & Decide**: Reject unsafe strategies (hard constraint engine) and score the remaining strategies based on buffer margin, speed, and simplicity.
- **Validate & Explain**: Deterministically validate the final output plan before producing `output.csv`.

## 3. Why this is an agent
It is an agent because it actively simulates future financial outcomes, generating and testing multiple decision pathways against environmental constraints rather than simply applying a static classifier.

## 4. Why rules + ML
Hard rules guarantee financial safety (protecting minimum balance). A statistical/ML model evaluates acceptable risks among safe options, ensuring the agent prioritizes safety over opaque probabilistic predictions.

## 5. Why day-by-day forecasting
A single balance snapshot misses future scheduled payments or salary drops that could unexpectedly put the user in financial distress before completion.

## 6. Media processing
Images are mapped to events to extract missing amounts. Messages are parsed for salary changes and date confirmations to correct historical assumptions.

## 7. Personalization
It uses individual constraints (`minimum_balance_to_keep`, preferred methods) to ensure decisions align with user risk tolerance.

## 8. Evaluation
Status Accuracy: 44.00%
Payment Method Accuracy: 44.00%
Constraint Violations: 0

## 9. Running
```bash
python3 code/main.py
```

## 10. Demo
```bash
python3 code/main.py --demo
```
