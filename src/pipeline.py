from .listing import get_all_listings_urls
from .details import scrape_all_details
from .saver import save_json
from .config import LISTING_PAGES


def run_pipeline(output_path="data/cfpb_docs.json"):

    listing_urls = get_all_listings_urls(LISTING_PAGES)
    records = scrape_all_details(listing_urls)
    save_json(records,output_path)
    return records
