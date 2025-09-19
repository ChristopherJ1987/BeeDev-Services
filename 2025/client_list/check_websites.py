"""
check_websites.py
- Read Yelp CSV (output from fetch_yelp.py)
- For each row:
    1) Try to find a website link on the Yelp business page
    2) If not found, try a small set of guessed domains
- Save updated CSV with website info
"""

import os
import re
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}

SOCIAL_DOMAINS = ("facebook.com", "instagram.com", "twitter.com", "linkedin.com", "youtube.com", "yelp.com", "google.com", "maps.google.com")

def slugify(s):
    s = s.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return s.strip("-")

def get_first_official_link_from_yelp(yelp_url):
    """Scrape the Yelp business page for an external website link (first non-social domain)."""
    try:
        r = requests.get(yelp_url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        # Find anchors and look for external domains that are not Yelp/social
        anchors = soup.find_all("a", href=True)
        candidates = []
        for a in anchors:
            href = a["href"].strip()
            if href.startswith("/"):
                continue
            # Normalize
            parsed = urlparse(href)
            domain = (parsed.netloc or "").lower().replace("www.", "")
            if not domain:
                continue
            if any(sd in domain for sd in SOCIAL_DOMAINS):
                continue
            # sometimes Yelp has redirect wrappers, skip known internal yelp redirect patterns
            if "yelp.com" in domain:
                continue
            candidates.append(href)
        # Return first candidate after sanity-checking it
        for link in candidates:
            if verify_match(link, None):  # quick check if reachable
                return link
        return None
    except Exception as e:
        # print("Yelp scrape error:", e)
        return None

def verify_match(url, name):
    """Check URL is reachable and (if name provided) has name word(s) in title/body."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        if r.status_code not in (200, 301, 302):
            return False
        content_type = r.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            return False
        if not name:
            return True
        text = r.text.lower()
        # look for at least one significant token from name in the page
        tokens = [t for t in re.split(r"\W+", name.lower()) if len(t) > 2]
        if not tokens:
            return True
        hits = sum(1 for t in tokens if t in text)
        return hits >= 1  # require at least one token present
    except Exception:
        return False

def guess_domains_and_check(name, city=None, max_try=6):
    """Generate likely domain names for the business and verify them."""
    slug = slugify(name)
    city_slug = slugify(city) if city else ""
    candidates = []
    # basic guesses
    if slug:
        candidates += [f"http://{slug}.com", f"http://www.{slug}.com"]
    if city_slug and slug:
        candidates += [f"http://{slug}-{city_slug}.com", f"http://{slug}{city_slug}.com"]
    # alternates
    candidates += [f"http://{slug}.net", f"http://{slug}.org"]
    # unique-ify and limit
    seen = set()
    final = []
    for c in candidates:
        if c in seen:
            continue
        seen.add(c)
        final.append(c)
        if len(final) >= max_try:
            break
    # check
    for url in final:
        try:
            if verify_match(url, name):
                return url
        except Exception:
            continue
        time.sleep(0.2)
    return None

def check_row(row):
    name = row.get("name") or ""
    city = row.get("city") or ""
    yelp_url = row.get("yelp_url") or ""

    # 1) try Yelp page scraping
    website = None
    method = None
    verified = False
    if yelp_url:
        website = get_first_official_link_from_yelp(yelp_url)
        if website:
            method = "from_yelp"
            verified = verify_match(website, name)

    # 2) if not found, try guessed domain(s)
    if not website:
        guessed = guess_domains_and_check(name, city)
        if guessed:
            website = guessed
            method = "guessed"
            verified = True

    if not website:
        method = "none"
        website = "NONE"
        verified = False

    return website, method, verified

def main(input_csv, output_csv=None):
    df = pd.read_csv(input_csv, dtype=str).fillna("")
    out_rows = []
    from tqdm import tqdm
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Checking websites"):
        website, method, verified = check_row(row)
        new_row = row.to_dict()
        new_row["website"] = website
        new_row["website_method"] = method
        new_row["website_verified"] = verified
        out_rows.append(new_row)
        # be polite / slow down
        time.sleep(random.uniform(0.4, 1.2))

    out_df = pd.DataFrame(out_rows)
    output_csv = output_csv or ("leads_with_websites.csv")
    out_df.to_csv(output_csv, index=False)
    print("Saved", output_csv)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="CSV from fetch_yelp.py")
    p.add_argument("--output", default="leads_with_websites.csv")
    args = p.parse_args()
    main(args.input, args.output)