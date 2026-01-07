# https://www.yelp.com/developers/v3/manage_app
    # the link above allows me to see api usage, and how many api calls are remaining for each month.
    # there are 5000 api calls alotted each month

# python fetch_yelp.py --term "whatever term" --location "City, ST" --max 100
    # the line above runs the fetch_yelp.py script, and then returns the list in a csv file


import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
YELP_API_KEY = os.getenv("YELP_API_KEY")
if not YELP_API_KEY:
    raise RuntimeError("Set YELP_API_KEY in .env")

SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
HEADERS = {"Authorization": f"Bearer {YELP_API_KEY}"}

def search_yelp(term, location, limit=50, max_results=200):
    businesses = []
    offset = 0
    while len(businesses) < max_results:
        params = {"term": term, "location": location, "limit": limit, "offset": offset}
        resp = requests.get(SEARCH_URL, headers=HEADERS, params=params, timeout=10)
        if resp.status_code == 429:
            print("Rate limited by Yelp. Sleeping 10s and retrying...")
            time.sleep(10)
            continue
        if resp.status_code != 200:
            print("Yelp API error:", resp.status_code, resp.text)
            break
        data = resp.json()
        batch = data.get("businesses", [])
        if not batch:
            break
        businesses.extend(batch)
        offset += len(batch)
        if len(batch) < limit:
            break
        time.sleep(0.5)  # be polite
    return businesses[:max_results]

def normalize_biz(biz):
    loc = biz.get("location") or {}
    categories = ", ".join([c.get("title","") for c in biz.get("categories", [])])
    return {
        "yelp_id": biz.get("id"),
        "name": biz.get("name"),
        "phone": biz.get("phone"),
        "display_phone": biz.get("display_phone"),
        "address": " ".join(loc.get("display_address", [])),
        "city": loc.get("city", ""),
        "state": loc.get("state", ""),
        "zip_code": loc.get("zip_code", ""),
        "categories": categories,
        "rating": biz.get("rating"),
        "review_count": biz.get("review_count"),
        "is_closed": biz.get("is_closed"),
        "yelp_url": biz.get("url"),
        "latitude": biz.get("coordinates", {}).get("latitude"),
        "longitude": biz.get("coordinates", {}).get("longitude")
    }

def fetch_and_save(term, location, max_results=100):
    print("Querying Yelp for", term, location)
    results = search_yelp(term, location, limit=50, max_results=max_results)
    rows = [normalize_biz(b) for b in results]
    df = pd.DataFrame(rows)
    safe_term = term.replace(" ", "_")
    safe_loc = location.replace(",", "").replace(" ", "_")
    filename = f"yelp_{safe_term}_{safe_loc}.csv"
    df.to_csv(filename, index=False)
    print("Saved", filename)
    return filename

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--term", required=True)
    p.add_argument("--location", required=True)
    p.add_argument("--max", type=int, default=100)
    args = p.parse_args()
    fetch_and_save(args.term, args.location, max_results=args.max)