import os
import re
import pandas as pd
from typing import Dict, Optional

class MediaExtractor:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.images_df = pd.read_csv(f"{data_dir}/images.csv")
        self.messages_df = pd.read_csv(f"{data_dir}/messages.csv")
        self.img_dir = f"{data_dir}/media/images"
        
        self.reader = None
        try:
            import easyocr
            # Use English, disable GPU if not available to save time
            self.reader = easyocr.Reader(['en'], gpu=False)
        except ImportError:
            print("Warning: easyocr not installed. Image extraction will be mocked/skipped.")

    def get_amount_from_event(self, event_id: str) -> Optional[float]:
        # Find if this event has an associated image
        row = self.images_df[self.images_df['related_event_id'] == event_id]
        if row.empty:
            return None
        
        image_id = row.iloc[0]['image_id']
        image_path = os.path.join(self.img_dir, f"{image_id}.png")
        
        if not os.path.exists(image_path):
            return None
            
        return self._extract_amount_from_image(image_path)
        
    def _extract_amount_from_image(self, image_path: str) -> Optional[float]:
        if not self.reader:
            return None
            
        try:
            results = self.reader.readtext(image_path, detail=0)
            text = " ".join(results)
            # Find amounts. Look for numbers, possibly with commas and decimals
            # typically preceded by currency symbols or codes, but we just need the largest or first number
            # that looks like an amount.
            # E.g., 1,234.56 or 1234
            matches = re.findall(r'(?:IDR|ZAR|EUR|INR|USD)?\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{1,2})?)', text)
            if matches:
                # heuristic: pick the largest number or the one that appears near "amount" or "total"
                # For simplicity in this mock/hackathon context, try to parse all and return the max or a specific one.
                # Let's clean the matches
                valid_amounts = []
                for m in matches:
                    clean_str = m.replace(',', '')
                    if '.' in clean_str and clean_str.count('.') > 1:
                        continue
                    try:
                        valid_amounts.append(float(clean_str))
                    except:
                        pass
                if valid_amounts:
                    # Often the total amount is the largest number on a receipt
                    return max(valid_amounts)
            return None
        except Exception as e:
            print(f"OCR Error on {image_path}: {e}")
            return None

    def get_messages_for_request(self, request_id: str) -> list:
        return self.messages_df[self.messages_df['request_id'] == request_id].to_dict('records')

    def get_messages_for_user(self, user_id: str) -> list:
        return self.messages_df[self.messages_df['user_id'] == user_id].to_dict('records')

    def get_messages_for_event(self, event_id: str) -> list:
        return self.messages_df[self.messages_df['related_event_id'] == event_id].to_dict('records')
