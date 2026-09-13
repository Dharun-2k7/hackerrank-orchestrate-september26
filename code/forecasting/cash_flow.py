from datetime import date, timedelta
from typing import List, Dict, Optional
import math
from dateutil.relativedelta import relativedelta
import re

from code.models import UserProfile, FinancialEvent, Request

class CashFlowSimulator:
    def __init__(self, user: UserProfile, events: List[FinancialEvent], messages: list):
        self.user = user
        self.events = events
        self.messages = messages
        
        # Parse messages for any salary changes or confirmed income
        self.salary_updates = self._parse_salary_messages(messages)

    def _parse_salary_messages(self, messages: list) -> list:
        updates = []
        for msg in messages:
            text = str(msg.get('message_text', '')).lower()
            if 'confirmed' in text or 'scheduled' in text or 'berlaku mulai' in text or 'continues' in text:
                # Basic heuristic for finding amounts and dates in messages
                matches = re.findall(r'(?:idr|zar|eur|inr|usd)?\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{1,2})?)', text, re.IGNORECASE)
                dates = re.findall(r'([0-9]{4}-[0-9]{2}-[0-9]{2})', text)
                if matches:
                    try:
                        amt_str = matches[0].replace(',', '')
                        amt = float(amt_str)
                        d = date.fromisoformat(dates[0]) if dates else None
                        updates.append({'amount': amt, 'date': d, 'text': text})
                    except:
                        pass
        return updates

    def simulate(self, 
                 start_date: date, 
                 days: int, 
                 payments: List[Dict[str, float]], 
                 spending_changes: List[str] = []) -> Dict:
        """
        Simulate balance for `days` starting from `start_date`.
        `payments` is a list of {'date': date, 'amount': float} in home currency.
        `spending_changes` is a list of changes e.g. "stop:event_id" or "reduce_to:event_id:amt".
        
        Returns:
            Dict containing min_balance, is_safe, etc.
        """
        current_balance = self.user.current_available_balance
        
        # Parse spending changes
        stopped_events = set()
        reduced_events = {}
        for sc in spending_changes:
            if not sc or sc == 'none':
                continue
            parts = sc.split(':')
            if parts[0] == 'stop' and len(parts) >= 2:
                stopped_events.add(parts[1])
            elif parts[0] == 'reduce_to' and len(parts) >= 3:
                reduced_events[parts[1]] = float(parts[2])
                
        # Generate all cash flows in the window
        end_date = start_date + timedelta(days=days)
        
        daily_flows = {start_date + timedelta(days=i): 0.0 for i in range(days+1)}
        
        for ev in self.events:
            # Skip if stopped
            if ev.event_id in stopped_events:
                continue
                
            amt = ev.normalized_amount or 0.0
            if ev.event_id in reduced_events:
                amt = reduced_events[ev.event_id]
                
            is_debit = (ev.direction == 'debit')
            val = -amt if is_debit else amt
            
            # 1. Handle pending or scheduled one-time events
            if ev.status in ['pending', 'scheduled'] and not ev.is_recurring:
                if ev.settlement_date >= start_date and ev.settlement_date <= end_date:
                    # Ignore pending credits/income per rules unless explicitly confirmed
                    if is_debit or 'income' in ev.category.lower(): # assuming safe
                        if is_debit:
                            daily_flows[ev.settlement_date] += val
                        else:
                            # Only count confirmed income
                            pass
                            
            # 2. Handle recurring events
            # (Heuristic: if it's settled multiple times in history on similar dates, or marked recurring)
            if ev.is_recurring:
                # We project recurring events based on their day of month
                # Just a simple monthly projection for hackathon
                d = ev.settlement_date
                while d <= end_date:
                    if d >= start_date:
                        # Override amount if message says it changed
                        proj_val = val
                        for upd in self.salary_updates:
                            if upd['date'] and d >= upd['date'] and not is_debit:
                                proj_val = upd['amount']
                                
                        # Essential expenses must be protected
                        daily_flows[d] += proj_val
                    d += relativedelta(months=1)
                    
        # Apply proposed payments
        for p in payments:
            if start_date <= p['date'] <= end_date:
                daily_flows[p['date']] -= p['amount']
                
        # Track balances
        min_bal = float('inf')
        balance = current_balance
        min_date = start_date
        
        for i in range(days+1):
            d = start_date + timedelta(days=i)
            balance += daily_flows[d]
            if balance < min_bal:
                min_bal = balance
                min_date = d
                
        is_safe = min_bal >= self.user.minimum_balance_to_keep
        
        return {
            'is_safe': is_safe,
            'min_balance': min_bal,
            'min_date': min_date,
            'ending_balance': balance
        }
