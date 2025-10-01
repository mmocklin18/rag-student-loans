import time
import json
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

BASE_URL = "https://osfa.uga.edu/resources/faqs/"
OUTPUT_FILE = "../data/uga_osfa_faqs.json"


def scrape_uga_faqs():
    faqs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL, timeout=60000)
        time.sleep(2)  # let JS render fully
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # Select all <h8 class="expList_title"> elements
    questions = soup.find_all("h8", class_="expList_title")
    print("FAQ blocks found:", len(questions))  # debug

    for q in questions:
        question_text = q.get_text(strip=True)

        # Find the next sibling with class exp_content
        answer_div = q.find_next_sibling("div", class_="exp_content")
        answer_text = ""
        if answer_div:
            answer_text = answer_div.get_text(" ", strip=True)

        if question_text and answer_text:
            faqs.append({
                "question": question_text,
                "answer": answer_text,
                "url": BASE_URL
            })

    return faqs

if __name__ == "__main__":
    faqs = scrape_uga_faqs()

    print(f"Scraped {len(faqs)} FAQs")
    with open(OUTPUT_FILE, "w") as f:
        json.dump(faqs, f, indent=2)
    print(f"Saved to {OUTPUT_FILE}")
