import sys
import string
import os

def extract_strings(filename, min_len=4):
    with open(filename, 'rb') as f:
        data = f.read()
    
    result = ""
    current_string = ""
    for b in data:
        c = chr(b)
        if c in string.printable:
            current_string += c
        else:
            if len(current_string) >= min_len:
                result += current_string + "\n"
            current_string = ""
    if len(current_string) >= min_len:
        result += current_string + "\n"
    return result

if __name__ == "__main__":
    img_dir = "dataset/media/images"
    for file in os.listdir(img_dir):
        if file.endswith(".png"):
            print(f"--- {file} ---")
            strs = extract_strings(os.path.join(img_dir, file), min_len=4)
            # print only lines containing digits or interesting words
            lines = [l for l in strs.split('\n') if any(c.isdigit() for c in l) or 'amount' in l.lower() or 'IDR' in l or 'ZAR' in l or 'EUR' in l or 'INR' in l or 'USD' in l]
            print("\n".join(lines[:10]))
