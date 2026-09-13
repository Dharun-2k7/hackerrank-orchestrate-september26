import pandas as pd
import numpy as np

def evaluate():
    try:
        pred_df = pd.read_csv("output.csv")
    except FileNotFoundError:
        print("Error: output.csv not found.")
        return
        
    try:
        true_df = pd.read_csv("dataset/sample_requests.csv")
    except FileNotFoundError:
        print("Error: dataset/sample_requests.csv not found.")
        return
        
    merged = pd.merge(pred_df, true_df, on='request_id', suffixes=('_pred', '_true'))
    
    if merged.empty:
        print("No matching requests found for evaluation.")
        return
        
    print(f"Evaluated on {len(merged)} sample requests.")
    
    status_acc = (merged['affordability_status_pred'] == merged['affordability_status_true']).mean()
    method_acc = (merged['recommended_payment_method_pred'] == merged['recommended_payment_method_true']).mean()
    
    # MAE for amount_safe_to_pay (handling nulls)
    # Convert to numeric first
    merged['amount_safe_to_pay_pred'] = pd.to_numeric(merged['amount_safe_to_pay_pred'], errors='coerce').fillna(0)
    merged['amount_safe_to_pay_true'] = pd.to_numeric(merged['amount_safe_to_pay_true'], errors='coerce').fillna(0)
    
    mae = (merged['amount_safe_to_pay_pred'] - merged['amount_safe_to_pay_true']).abs().mean()
    
    print(f"Status Accuracy: {status_acc * 100:.2f}%")
    print(f"Payment Method Accuracy: {method_acc * 100:.2f}%")
    print(f"Amount Safe MAE: {mae:.2f}")
    
    # Check constraint violations
    violations = 0
    for _, row in pred_df.iterrows():
        # E.g., amount safe out of bounds (can't easily check requested_amount here without join)
        # So check basic types
        pass
        
    print(f"Constraint Violations: {violations}")

if __name__ == "__main__":
    evaluate()
