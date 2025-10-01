from typing import List
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from ..config import BASE_URL

def get_all_listings_urls(listing_pages: List[str]) -> List[str]:
    """
    Visit each listing page in `listing_pages`, extract CFPB Q&A links
    from `section.results article a`, and return list of all resulting urls
    
    Returns:
        List[str] - URLs of Q&A pages from CFPB website.
    """

    page_urls = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        chromium_page = browser.new_page()

        for lp in listing_pages:
            try:
                # go to url
                chromium_page.goto(lp, timeout=30000)
                # wait to render main (id=main)
                chromium_page.wait_for_selector("main#main", timeout=10000)
                # get html from main
                html = chromium_page.inner_html("main#main")

            except PlaywrightTimeoutError:
                print(f"ERROR: timeout loading listing page: {lp}")
                continue
            except Exception as e:
                print(f"ERROR: error loading listing page {lp}: {e}")
                continue

            #parse HTML
            soup = BeautifulSoup(html, "html.parser")

            curr_page = []

            #select inner anchor tags to extract hrefs from search results
            for a in soup.select("section.results article a"):
                href = a.get("href")
                if href and href.startswith("/ask-cfpb/"):
                    curr_page.append(BASE_URL + href)

            #add this pages results to overall list
            page_urls.extend(curr_page)
            print(f"Found {len(curr_page)} links on {lp}")
            time.sleep(0.6)

        browser.close()

    #remove any duplicates
    unique_urls = list(dict.fromkeys(page_urls))

    return unique_urls