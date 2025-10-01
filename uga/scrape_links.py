import json
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

BASE_URL = "https://osfa.uga.edu/resources/policies/enrollment-financial-aid/"
OUTPUT_FILE = "../data/uga_enrollment_policies.json"

#Get all boxed sublinks from the main page
def get_sublinks(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_selector("div.portal_item", timeout=30000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    links = []
    for a in soup.select("div.portal_item div.box_hover a"):
        href = a.get("href")
        title = a.select_one("h5.portal_title")
        title_text = title.get_text(strip=True) if title else ""
        if href:
            links.append((href, title_text))

    return list(set(links))

# Scrape each policy page into Q/A-like docs
def scrape_policy_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        time.sleep(2)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    docs = []

    entry = soup.select_one("div.entry")
    if not entry:
        return docs  # no content

    # Case 1: structured headings
    headers = entry.select("h2, h3")
    if headers:
        for section in headers:
            header = section.get_text(strip=True)
            content = []
            for sib in section.find_next_siblings():
                if sib.name in ["h2", "h3"]:
                    break
                if sib.name == "p":
                    content.append(sib.get_text(" ", strip=True))
            if content:
                docs.append({
                    "question": header,
                    "answer": " ".join(content),
                    "url": url
                })
    else:
        # Case 2: just paragraphs
        paragraphs = [p.get_text(" ", strip=True) for p in entry.select("p")]
        if paragraphs:
            # Try page <title> or h1 as the "question"
            page_title = soup.title.string if soup.title else "UGA Policy Page"
            docs.append({
                "question": page_title,
                "answer": " ".join(paragraphs),
                "url": url
            })

    return docs


# Step 3: Crawl and save
if __name__ == "__main__":
    print(f"Getting sublinks from {BASE_URL} ...")
    sublinks = get_sublinks(BASE_URL)
    print(f"Found {len(sublinks)} sublinks")
    
    all_docs = []
    for href, title in sublinks:
        #print(f"Scraping {href} ({title})")
        try:
            all_docs.extend(scrape_policy_page(href))
        except Exception as e:
            print(f"Failed to scrape {href}: {e}")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_docs, f, indent=2)

    print(f"Scraped {len(all_docs)} sections and saved to {OUTPUT_FILE}")
