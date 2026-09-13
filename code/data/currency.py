import pandas as pd
from datetime import date
from typing import Dict, Tuple

class CurrencyConverter:
    def __init__(self, exchange_rates_df: pd.DataFrame):
        # exchange_rates_df has: rate_date, from_currency, to_currency, rate
        self.rates = exchange_rates_df.copy()
        if not self.rates.empty:
            self.rates['rate_date'] = pd.to_datetime(self.rates['rate_date']).dt.date
            # Sort by date descending so we can easily find the prior rate
            self.rates = self.rates.sort_values(by='rate_date', ascending=False)
            
        # Group by currency pairs for faster lookup
        self.grouped_rates = {}
        for (from_curr, to_curr), group in self.rates.groupby(['from_currency', 'to_currency']):
            self.grouped_rates[(from_curr, to_curr)] = group

    def convert(self, amount: float, from_curr: str, to_curr: str, target_date: date) -> float:
        if pd.isna(amount):
            return amount
        if from_curr == to_curr:
            return float(amount)
        
        pair = (from_curr, to_curr)
        if pair not in self.grouped_rates:
            # Try inverse if direct doesn't exist, though dataset should have correct direction
            inverse_pair = (to_curr, from_curr)
            if inverse_pair in self.grouped_rates:
                rate = self._get_rate(inverse_pair, target_date)
                if rate:
                    return float(amount / rate)
            # If no rate is found, raise error or return amount (depends on constraints)
            # "Never invent rates"
            raise ValueError(f"No exchange rate found for {from_curr} to {to_curr}")
            
        rate = self._get_rate(pair, target_date)
        if rate is None:
            raise ValueError(f"No exchange rate found prior to {target_date} for {from_curr} to {to_curr}")
            
        return float(amount * rate)
        
    def _get_rate(self, pair: Tuple[str, str], target_date: date) -> float:
        group = self.grouped_rates[pair]
        # Find the first rate where rate_date <= target_date
        # Since it's sorted descending, the first one that matches is the latest valid prior rate
        for _, row in group.iterrows():
            if row['rate_date'] <= target_date:
                return row['rate']
        return None
