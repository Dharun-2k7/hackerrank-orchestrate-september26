import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import argparse
import pandas as pd
import time

from code.data.loader import DataLoader
from code.data.currency import CurrencyConverter
from code.media.extractor import MediaExtractor
from code.decision.agent import DecisionAgent

def main():
    parser = argparse.ArgumentParser(description="Buy or Wait? AI Financial Agent")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")
    parser.add_argument("--eval", action="store_true", help="Run on sample requests for evaluation")
    args = parser.parse_args()
    
    start_time = time.time()
    data_dir = "dataset"
    
    loader = DataLoader(data_dir)
    if args.eval:
        loader.requests_df = pd.read_csv(f"{data_dir}/sample_requests.csv")
    media = MediaExtractor(data_dir)
    currency = CurrencyConverter(pd.read_csv(f"{data_dir}/exchange_rates.csv"))
    
    agent = DecisionAgent(loader, media, currency)
    
    outputs = []
    
    for req in agent.requests:
        rec = agent.process_request(req, demo=args.demo)
        
        outputs.append({
            'request_id': rec.request_id,
            'amount_safe_to_pay': rec.amount_safe_to_pay,
            'affordability_status': rec.affordability_status,
            'recommended_payment_method': rec.recommended_payment_method,
            'payment_plan': rec.payment_plan,
            'earliest_date_for_full_payment': rec.earliest_date_for_full_payment,
            'spending_changes_needed': rec.spending_changes_needed,
            'decision_explanation': rec.decision_explanation
        })
        
    df = pd.DataFrame(outputs)
    # Ensure exact column order
    cols = ['request_id', 'amount_safe_to_pay', 'affordability_status', 'recommended_payment_method',
            'payment_plan', 'earliest_date_for_full_payment', 'spending_changes_needed', 'decision_explanation']
    df = df[cols]
    
    df.to_csv("output.csv", index=False)
    
    end_time = time.time()
    
    if not args.demo:
        print(f"Generated output.csv with {len(df)} rows in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
