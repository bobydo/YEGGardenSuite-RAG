from urllib.parse import urlparse
from duckduckgo_search import DDGS

ALLOWED = {"zoningbylaw.edmonton.ca", "www.edmonton.ca"}  # keep it tight

QUERIES = [
    # with site filters (preferred)
    'site:zoningbylaw.edmonton.ca "Backyard Housing" 6.10',
    'site:zoningbylaw.edmonton.ca "Measuring Height and Grade" 5.70',
    'site:www.edmonton.ca backyard housing permits setbacks',

    # optional broader query (fallback discovery)
    'Edmonton backyard housing height width bylaw',
]

def search_urls(queries, k=8):
    hits = []
    with DDGS() as ddg:
        for q in queries:
            hits += ddg.text(q, max_results=k)
    urls = [h["href"] for h in hits if "href" in h]
    # allowlist gate
    return [u for u in urls if urlparse(u).netloc in ALLOWED]

urls = search_urls(QUERIES)
for url in sorted(urls):
    print(f'"{url}",')