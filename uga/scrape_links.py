import os
import json
import time
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

BASE_URL = "https://osfa.uga.edu/resources/policies/"
OUTPUT_FILE = "../data/uga_policies.json"


def allowed(u: str) -> bool:
    try:
        p = urlparse(u)
        return p.netloc == "osfa.uga.edu" and p.path.startswith("/resources/policies/")
    except Exception:
        return False


def scrape_leaf(url: str, page) -> list:
    """Scrape text content from a leaf page (no box links)."""
    page.goto(url, timeout=60000)
    time.sleep(2)
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Collect text from leaf page
    paragraphs = [p.get_text(" ", strip=True) for p in soup.select("div.entry p")]
    text = " ".join(paragraphs)
    docs = []
    if text:
        title = soup.title.get_text(strip=True) if soup.title else url.split("/")[-2]
        docs.append({
            "question": title,
            "answer": text,
            "url": url
        })
    return docs


def crawl_boxes(url: str, page, visited: set, all_docs: list):
    """DFS crawl: follow portal box links; if none, scrape this page."""
    norm = url.split("#")[0]
    if norm in visited:
        return
    visited.add(norm)

    print(f"\n Visiting: {url}")
    page.goto(url, timeout=60000)
    try:
        page.wait_for_selector("div.portal_item, div.entry, main#main, article", timeout=15000)
    except Exception:
        pass

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    #find box links
    box_links = []
    for a in soup.select("div.portal_item div.box_hover a"):
        href = a.get("href")
        if not href:
            continue
        full = urljoin(url, href)
        if allowed(full):
            box_links.append(full)

    box_links = sorted(set(box_links))

    # If any box links are found, recursively search deeper
    if box_links:
        print(f"  + {len(box_links)} box link(s) found")
        for link in box_links:
            time.sleep(10)  # respect crawl-delay
            crawl_boxes(link, page, visited, all_docs)

    # Base case: if no more links, scrape page for docs
    else:
        try:
            docs = scrape_leaf(url, page)
            if docs:
                print(f"scraped {len(docs)} doc(s)")
                all_docs.extend(docs)
            else:
                print("no docs extracted")
        except Exception as e:
            print(f"scrape failed: {e}")


if __name__ == "__main__":
    visited = set()
    all_docs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        crawl_boxes(BASE_URL, page, visited, all_docs)
        browser.close()

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_docs, f, indent=2)

    print(f"\nDone. Visited {len(visited)} pages, scraped {len(all_docs)} sections.")
    print(f"Saved to {OUTPUT_FILE}")
