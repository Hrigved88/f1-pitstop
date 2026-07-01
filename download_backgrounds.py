import pandas as pd
import urllib.request
import urllib.parse
import re
import os
import json
import time

def fetch_circuit_image_url(circuit_name):
    query = f"{circuit_name} F1 aerial view"
    url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
        m = re.search(r'murl&quot;:&quot;(.*?)&quot;', html)
        if m:
            return m.group(1)
    except Exception as e:
        print(f"Error fetching {circuit_name}: {e}")
    return None

def main():
    if not os.path.exists("circuits.csv"):
        print("circuits.csv not found!")
        return

    circuits = pd.read_csv("circuits.csv")
    os.makedirs("circuit_backgrounds", exist_ok=True)
    
    # We will just fetch the URLs and save them to a JSON mapping to avoid downloading large files locally
    # Streamlit can render background images directly from URLs!
    url_mapping = {}
    
    # Load existing to avoid re-fetching if we stop/start
    if os.path.exists("circuit_bg_map.json"):
        with open("circuit_bg_map.json", "r") as f:
            url_mapping = json.load(f)

    for index, row in circuits.iterrows():
        c_id = str(row['circuitId'])
        c_name = row['name']
        if c_id in url_mapping and url_mapping[c_id]:
            continue
            
        # Avoid unicode print errors on Windows
        c_name_safe = c_name.encode('ascii', 'ignore').decode('ascii')
        print(f"Fetching URL for {c_name_safe}...")
        
        # Improved query to try and avoid random unrelated images
        query = f"{c_name} Formula 1 race track aerial photo"
        url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        img_url = None
        try:
            html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
            m = re.search(r'murl&quot;:&quot;(.*?)&quot;', html)
            if m:
                img_url = m.group(1)
        except Exception as e:
            pass
            
        if img_url:
            url_mapping[c_id] = img_url
            print(f"Found image for {c_name_safe}")
        else:
            print(f"Failed to find image for {c_name_safe}")
        
        # Save incrementally
        with open("circuit_bg_map.json", "w") as f:
            json.dump(url_mapping, f, indent=4)
            
        time.sleep(1) # Be nice to Bing

    print("Finished fetching all background URLs!")

if __name__ == "__main__":
    main()
