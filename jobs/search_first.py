
# search_first.py
# Discover authoritative URLs for Edmonton backyard housing Q&A.
# Includes ALL residential zones by default.
# Prints two groups: "PDF urls" (ending with .pdf) and "Other urls".
#
# Usage:
#   python search_first.py -k 25 --mine
#

# Deps:
#   pip install duckduckgo-search beautifulsoup4 requests
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import argparse, json, re, time
from urllib.parse import urlparse
import requests
from ddgs import DDGS
from bs4 import BeautifulSoup
from service.utils import download_pdf
from config import LOGS_DIR

ALLOWED = {"zoningbylaw.edmonton.ca", "www.edmonton.ca"}

PDF_URL_RE = re.compile(r'\.pdf(?:$|[?#/])', re.I)

# Always include this URL in results (per request)
ALWAYS_INCLUDE = "https://www.edmonton.ca/programs_services/housing/affordable-housing-developments"

# ---- Tunable mining pattern (internal string) ----
# Captures common lane/pathway/vehicle-access phrases found in bylaw/guide pages.
ACCESS_TERMS_REGEX = r"\b(?:abutting lane|rear lane|back lane|pathway|vehicle access)\b"  # case-insensitive

# (Optional) keep a couple of generic capitalized phrase patterns for headings/terms discovery
CAPITALIZED_BIGRAM_REGEX  = r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"
CAPITALIZED_TRIGRAM_REGEX = r"\b[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+\b"

# ---- Glossary (ALL zones) ----
GLOSSARY = {
    "alley": ["alley", "lane", "laneway", "rear lane", "back lane"],
    "ped_access": ["pathway", "walkway", "sidewalk", "hard-surfaced pathway", '"0.9 m" pathway'],
    "veh_access": ["vehicle access", "driveway", "garage access"],
    "object": ["backyard housing", '"Backyard Housing"', '"Garden Suite"'],
    "bylaw_refs": ['"6.10"', '"5.70"', '"Measuring Height and Grade"'],
    "zones": [
        "RS", "RSF", "RSM", "RM", "RL", "RR",
        '"Small Scale Residential Zone"',
        '"Small Scale Flex Residential Zone"',
        '"Small-Medium Scale Transition Residential Zone"',
        '"Medium Scale Residential Zone"',
        '"Large Scale Residential Zone"',
        '"Rural Residential Zone"',
    ],
}

BASE_QUERIES = [
    "Do I need an alley for a backyard house?",
    "alley requirement backyard housing edmonton",
    "pathway requirement backyard housing edmonton 0.9 m",
]

SITE_TEMPLATES = [
    'site:zoningbylaw.edmonton.ca {q}',
    'site:www.edmonton.ca {q}',
]

def allowlist(urls):
    return [u for u in urls if urlparse(u).netloc in ALLOWED]

def ddg(q, k=20):
    for _ in range(2):
        try:
            with DDGS() as ddg:
                return [r.get("href") for r in ddg.text(q, max_results=k) if r.get("href")]
        except Exception:
            time.sleep(0.5)
    return []

def gen_queries():
    zones = GLOSSARY["zones"]
    combos = []

    # Mix alley/lane + pedestrian/vehicle access + object (kept compact)
    for a in GLOSSARY["alley"]:
        for pa in ["pathway", '"0.9 m" pathway', "sidewalk"]:
            q = f'{a} {pa} ({" OR ".join(GLOSSARY["veh_access"])}) ({" OR ".join(GLOSSARY["object"])})'
            combos.append(q)

    # Zone-aware queries (ALL zones)
    combos.append(f'( {" OR ".join(zones)} ) (alley OR lane OR "vehicle access" OR driveway) "Backyard Housing"')
    combos.append(f'( {" OR ".join(zones)} ) ("Pathway" OR sidewalk OR walkway OR "0.9 m") "Backyard Housing"')

    # Bylaw section references
    combos.append(f'( {" OR ".join(GLOSSARY["alley"])} ) ({" OR ".join(GLOSSARY["bylaw_refs"])}) "Backyard Housing"')

    # Base paraphrases
    combos += BASE_QUERIES

    # Wrap with site filters + dedupe
    candidates = []
    for q in combos:
        for tmpl in SITE_TEMPLATES:
            candidates.append(tmpl.format(q=q))

    seen, final = set(), []
    for q in sorted(candidates, key=len):
        if q not in seen:
            final.append(q); seen.add(q)
    return final

def scrape_terms(url, timeout=12):
    # Mine new terms from pages (case-insensitive)
    try:
        headers = {"User-Agent": os.getenv("USER_AGENT", "YEGGardenSuite-RAG/1.0")}
        html = requests.get(url, timeout=timeout, headers=headers).text
        soup = BeautifulSoup(html, "html.parser")
        text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))

        patterns = [
            CAPITALIZED_BIGRAM_REGEX,
            CAPITALIZED_TRIGRAM_REGEX,
            ACCESS_TERMS_REGEX,
        ]

        hits = set()
        for pat in patterns:
            try:
                # Use IGNORECASE to match "Pathway" and "pathway" etc.
                hits.update(re.findall(pat, text, flags=re.IGNORECASE))
            except re.error as e:
                print(f"[warn] bad regex skipped: {pat} -> {e}")

        # Normalize tuples to strings, dedupe, trim
        out = []
        for h in hits:
            if isinstance(h, tuple):
                out.append(" ".join([x for x in h if isinstance(x, str)]).strip())
            elif isinstance(h, str):
                out.append(h.strip())
        return sorted({x for x in out if x})[:100]
    except Exception:
        return []
def is_pdf (url):
    is_pdf = bool(__import__('re').search(r'\.pdf(?:$|[?#/])', url.lower()))
    return is_pdf

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-k", type=int, default=25, help="max results per query (default: 25)")
    ap.add_argument("--mine", action="store_true", help="mine new terms from top pages")
    args = ap.parse_args()

    queries = gen_queries()
    results = {}
    all_urls = set()

    for q in queries:
        urls = allowlist(ddg(q, k=args.k))
        if urls:
            results[q] = urls
            all_urls.update(urls)
        time.sleep(0.2)  # polite

    # Always include requested URL
    all_urls.add(ALWAYS_INCLUDE)

    # Optional: mine terms
    mined = {}
    if args.mine:
        for u in sorted(all_urls):
            mined[u] = scrape_terms(u)
            time.sleep(0.2)

    # Partition PDFs vs others
    pdf_urls = []
    other_urls = []
    for u in sorted(all_urls):
        try:
            path = urlparse(u).path.lower()
            if is_pdf(path):
                pdf_url_print_format = f"\"{u}\","
                print(pdf_url_print_format)
                pdf_urls.append(pdf_url_print_format)
            else:
                other_urls_print_format = f"\"{u}\","
                print(other_urls_print_format)
                other_urls.append(other_urls_print_format)
        except Exception:
            other_urls.append(u)

    # Print grouped output
    print(f"PDF urls ({len(pdf_urls)}):")
    for u in pdf_urls:
        print(u)
        saved = download_pdf(u)
        if saved:
            print("Saved to:", saved)
        else:
            print(f"[error] PDF not saved for: {u}")

    print(f"\nOther urls ({len(other_urls)}):")
    for u in other_urls:
        print(u)

    # Save artifacts
    with open(LOGS_DIR / "search_first_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "queries": queries,
            "unique_urls": sorted(all_urls),
            "pdf_urls": pdf_urls,
            "other_urls": other_urls,
            "mined_terms": mined if args.mine else {},
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
