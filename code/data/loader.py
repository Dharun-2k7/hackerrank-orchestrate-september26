import pandas as pd
import numpy as np
from datetime import date
from typing import List, Dict
import math

from code.models import UserProfile, FinancialEvent, Request, PaymentOption

class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.profiles_df = pd.read_csv(f"{data_dir}/financial_profiles.csv")
        self.events_df = pd.read_csv(f"{data_dir}/financial_events.csv")
        self.requests_df = pd.read_csv(f"{data_dir}/requests.csv")
        self.options_df = pd.read_csv(f"{data_dir}/request_payment_options.csv")
        self.exchange_rates_df = pd.read_csv(f"{data_dir}/exchange_rates.csv")
        self.messages_df = pd.read_csv(f"{data_dir}/messages.csv")
        self.images_df = pd.read_csv(f"{data_dir}/images.csv")

    def _split_str(self, val) -> List[str]:
        if pd.isna(val) or str(val).strip() == "":
            return []
        return [v.strip() for v in str(val).split('|') if v.strip()]

    def load_users(self) -> Dict[str, UserProfile]:
        users = {}
        for _, row in self.profiles_df.iterrows():
            user = UserProfile(
                user_id=row['user_id'],
                home_currency=row['home_currency'],
                current_available_balance=float(row['current_available_balance']),
                minimum_balance_to_keep=float(row['minimum_balance_to_keep']),
                financial_priorities=self._split_str(row['financial_priorities']),
                expense_categories_to_protect=self._split_str(row['expense_categories_to_protect']),
                expense_categories_user_is_willing_to_reduce=self._split_str(row.get('expense_categories_user_is_willing_to_reduce', '')),
                expense_categories_user_is_willing_to_stop=self._split_str(row.get('expense_categories_user_is_willing_to_stop', '')),
                payment_methods_user_will_consider=self._split_str(row['payment_methods_user_will_consider']),
                max_installment_months=int(row['max_installment_months']) if not pd.isna(row.get('max_installment_months')) else None
            )
            users[user.user_id] = user
        return users

    def load_requests(self) -> List[Request]:
        requests = []
        for _, row in self.requests_df.iterrows():
            req = Request(
                request_id=row['request_id'],
                user_id=row['user_id'],
                request_date=pd.to_datetime(row['request_date']).date(),
                request_type=row['request_type'],
                requested_amount=float(row['requested_amount']),
                desired_completion_date=pd.to_datetime(row['desired_completion_date']).date(),
                allows_partial_payment=str(row['allows_partial_payment']).strip().lower() == 'true',
                request_text=str(row['request_text'])
            )
            requests.append(req)
        return requests

    def load_payment_options(self) -> Dict[str, List[PaymentOption]]:
        options = {}
        for _, row in self.options_df.iterrows():
            opt = PaymentOption(
                payment_option_id=row['payment_option_id'],
                request_id=row['request_id'],
                payment_method=row['payment_method'],
                payment_amount=float(row['payment_amount']),
                number_of_payments=int(row['number_of_payments']),
                first_payment_date=pd.to_datetime(row['first_payment_date']).date(),
                payment_frequency_days=int(row.get('payment_frequency_days', 30)) if not pd.isna(row.get('payment_frequency_days')) else 0,
                financing_fee=float(row.get('financing_fee', 0)),
                total_payable_amount=float(row['total_payable_amount'])
            )
            if opt.request_id not in options:
                options[opt.request_id] = []
            options[opt.request_id].append(opt)
        return options

    def load_events(self) -> Dict[str, List[FinancialEvent]]:
        events = {}
        for _, row in self.events_df.iterrows():
            amt = None if pd.isna(row['amount']) else float(row['amount'])
            min_amt = None if pd.isna(row.get('minimum_allowed_amount')) else float(row['minimum_allowed_amount'])
            ev = FinancialEvent(
                event_id=row['event_id'],
                user_id=row['user_id'],
                event_type=row['event_type'],
                description=str(row['description']),
                category=row['category'],
                direction=row['direction'],
                amount=amt,
                currency=row['currency'],
                event_date=pd.to_datetime(row['event_date']).date(),
                settlement_date=pd.to_datetime(row['settlement_date']).date(),
                status=row['status'],
                linked_event_id=str(row['linked_event_id']) if not pd.isna(row['linked_event_id']) else None,
                flexibility=row['flexibility'],
                minimum_allowed_amount=min_amt
            )
            if ev.user_id not in events:
                events[ev.user_id] = []
            events[ev.user_id].append(ev)
        return events
