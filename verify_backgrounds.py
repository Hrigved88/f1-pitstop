import json
import urllib.request
from collections import Counter

def check_image(url):
    try:
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=3)
        return res.status == 200 and 'image' in res.getheader('Content-Type', '')
    except Exception as e:
        return False

def main():
    try:
        with open('circuit_bg_map.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: circuit_bg_map.json not found.")
        return

    urls = list(data.values())
    
    # 1. Check for duplicates
    url_counts = Counter(urls)
    duplicates = {url: count for url, count in url_counts.items() if count > 1}
    
    if duplicates:
        print(f"Found {len(duplicates)} duplicate image URLs.")
        for url, count in duplicates.items():
            print(f" - {url} appears {count} times")
    else:
        print("Awesome! No duplicate image URLs found. Every circuit got a unique image.")

    # 2. Check for broken links (optional fast check, might take ~20s)
    print("\nChecking if URLs are valid images (this may take a moment)...")
    broken_circuits = []
    
    valid_data = {}
    
    for c_id, url in data.items():
        if url in duplicates:
            print(f"Warning: Removing circuit {c_id} because its URL is a duplicate.")
        elif not check_image(url):
            safe_url = url.encode('ascii', 'ignore').decode('ascii')
            print(f"Warning: Removing circuit {c_id} because URL is broken or not an image: {safe_url}")
            broken_circuits.append(c_id)
        else:
            valid_data[c_id] = url
            
    print(f"\nFinished verification! Kept {len(valid_data)} valid, unique images out of 79.")
    
    # Save the cleaned map
    with open('circuit_bg_map.json', 'w') as f:
        json.dump(valid_data, f, indent=4)
        
    print("Cleaned map saved successfully.")

if __name__ == '__main__':
    main()
