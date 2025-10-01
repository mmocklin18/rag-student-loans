from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time
from ..config import CFPB_BOILERPLATE


def scrape_all_details(urls):
    docs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
    
        for url in urls:
            try:
                page.goto(url, timeout=30000)
                page.wait_for_selector("main#main", timeout=10000)
                html = page.inner_html("main#main")
            except Exception as e:
                print(f"Error failed to load {url}: {e}")
                continue

            soup = BeautifulSoup(html, "html.parser")

            # get question
            question = soup.find("h1").get_text(strip=True) if soup.find("h1") else ""
            paragraphs = []

            # get paragraph text (answers) and clean out boilerplate
            for ptag in soup.find_all("p"):
                t = ptag.get_text(" ", strip=True)
                if not t or any(snip in t for snip in CFPB_BOILERPLATE):
                    continue
                paragraphs.append(t)
            answer = "\n\n".join(paragraphs)

            docs.append({
                "url": url,
                "question": question,
                "answer": answer
            })

            time.sleep(0.6)  
        browser.close()
    return docs