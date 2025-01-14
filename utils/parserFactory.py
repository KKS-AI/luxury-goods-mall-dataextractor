import os
import logging
import time
import pandas as pd
from bs4 import BeautifulSoup
from utils.htmlFactory import download_full_html, extract_product_details_from_html
from config.rebag import global_product_elements_class_name

# Setup logger
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,  # You can change this to DEBUG, ERROR, etc.
    handlers=[
        logging.StreamHandler(),  # Logs to console
        logging.FileHandler('scraper.log', mode='a')  # Logs to a file 'scraper.log'
    ]
)
logger = logging.getLogger(__name__)

class RebagListScraper:
    def __init__(self, product_category, output_csv_file_path, page_range):
        self.product_category = product_category
        self.output_csv_file_path = output_csv_file_path
        self.page_range = page_range

    def scrape(self):
        all_products = []
        temp_dir = './tmp'
        os.makedirs(temp_dir, exist_ok=True)
        logger.info(f"Starting scrape for category: {self.product_category}.")

        for page_number in self.page_range:
            base_url = f'https://shop.rebag.com/collections/all-{self.product_category}?page={page_number}'
            file_path = os.path.join(temp_dir, f"rebag-all-{self.product_category}-mainpage{page_number}.html")
            
            logger.info(f"Downloading page {page_number} from {base_url}")
            self._download_page(base_url, file_path)

            with open(file_path, 'r', encoding='utf-8') as f:
                html = f.read()

            products = extract_product_details_from_html(html)
            all_products.extend(products)

            # Optional: Wait between requests to prevent overloading the server
            time.sleep(2)

            self._save_to_csv(all_products)
            logger.info(f"Page {page_number} done. Saved products to CSV.")
            os.remove(file_path)

        os.removedirs(temp_dir)
        logger.info(f"Data extraction complete. Products saved to {self.output_csv_file_path}.")

    def _download_page(self, url, file_path):
        """Helper method to download HTML content."""
        download_full_html(url, file_path, global_product_elements_class_name)

    def _save_to_csv(self, all_products):
        """Helper method to save products to CSV."""
        df = pd.DataFrame(all_products)
        df.to_csv(self.output_csv_file_path, mode='a', header=False, index=False)



def products_info_scrape(html_file):
    # Load the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        content = file.read()
    file_name = os.path.basename(html_file)
    # Parse HTML content with BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    # Initialize dictionary for product details
    product_data = {'filename': file_name}

    # Extract Condition details
    condition_section = soup.find('div', {'class': 'pdp__section pdp__section--conditions', 'id': 'pdp__section--conditions'})
    if condition_section:
        condition_selected = condition_section.find('li', {'class': 'pdp__condition-item pdp__condition-item--selected'})
        if condition_selected:
            product_data['Condition'] = condition_selected.text.strip()
        condition_details = condition_section.find('div', {'class': 'pdp__condition-text'})
        if condition_details:
            product_data['Condition Details'] = condition_details.text.strip()

    # Extract Size and Fit details
    size_and_fit_section = soup.find('div', {'class': 'pdp__section pdp__section--size-and-fit', 'id': 'pdp__section--size-and-fit'})
    if size_and_fit_section:
        for group in size_and_fit_section.find_all('div', {'class': 'pdp__group-item'}):
            key_value = group.text.split(":")
            if len(key_value) == 2:
                product_data[key_value[0].strip()] = key_value[1].strip()

    # Extract Overview details
    overview_section = soup.find('div', {'class': 'pdp__section pdp__section--overview', 'id': 'pdp__section--overview'})
    if overview_section:
        for group in overview_section.find_all('div', {'class': 'pdp__section-group'}):
            title = group.find('div', {'class': 'pdp__group-title'}).text.strip()
            
            # Handle "Accessories" as a special case to join items with commas
            if title == "Accessories":
                items = group.find_all('div', {'class': 'pdp__group-item pdp__group-item--li'})
                accessories_list = [item.text.strip() for item in items]
                product_data[title] = ", ".join(accessories_list)
            else:
                item = group.find('div', {'class': 'pdp__group-item'}).text.strip()
                product_data[title] = item

    # Extract Serial Number, Reference Number, and CLAIR CODE
    no_title_section = soup.find('div', {'class': 'pdp__section pdp__section--no-title'})
    if no_title_section:
        for group in no_title_section.find_all('div', {'class': 'pdp__section-group'}):
            title = group.find('div', {'class': 'pdp__group-title'}).text.strip()
            item = group.find('div', {'class': 'pdp__group-item'}).text.strip()
            product_data[title] = item

    # Extract Image URLs
    image_urls = []
    image_section = soup.find_all('div', {'class': 'pdp__mobile-image slick-slide'})
    for image in image_section:
        img_tag = image.find('img', {'class': 'slick-loading'})
        if img_tag and img_tag.has_attr('data-lazy'):
            image_url = "https:" + img_tag['data-lazy']
            image_urls.append(image_url)
    return product_data, image_urls
