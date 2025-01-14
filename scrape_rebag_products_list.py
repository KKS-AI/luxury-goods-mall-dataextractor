import argparse
from utils.parserFactory import RebagListScraper


if __name__ == '__main__':
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Scrape products from Rebag website.')
    parser.add_argument('--product_category', type=str, help='Category of products to scrape (e.g., "bags", "watches")', default='bags')
    parser.add_argument('--output_csv_file_path', type=str, help='Output CSV file path to save scraped products', default='rebag_products.csv')
    parser.add_argument('--page_range', type=str, help='Page range in the format "start,end" (e.g., "1,200")', default='1,200')

    args = parser.parse_args()

    product_category = args.product_category
    output_csv_file_path = args.output_csv_file_path
    start, end = map(int, args.page_range.split(','))
    page_range = range(start, end + 1)

    scraper = RebagListScraper(product_category, output_csv_file_path, page_range)      
    scraper.scrape()
