import os
import re
import argparse
import pandas as pd
from utils.parserFactory import products_info_scrape as scrape
from utils.dbFactory import DatabaseManager

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Extract product details from HTML files and save to database.')
    parser.add_argument('--product_category', type=str, help='Category of products to scrape (e.g., "bags", "watches")', required=True)
    parser.add_argument('--product_list_csv', type=str, help='Path to the CSV file with product links and details', required=True)
    parser.add_argument('--output_dir_path', type=str, help='Directory to save the product HTML files', required=True)

    return parser.parse_args()


def process_product_data(df, output_dir_path, category):
     # Initialize DatabaseManager
    db_manager = DatabaseManager(category)
    """Process and store product data in the database."""
    for i in range(0, len(df)):
        url = df['Link'][i]
        title = df['Title'][i]
        brand = df['Designer'][i]
        condition = df['Condition'][i]
        price = df['Price'][i]

        file_path = os.path.join(output_dir_path, f"index_{i}_{title}_{brand}_{condition}_{price}.html")

        # Extract product details
        product_data, image_urls = scrape(file_path)

        # Ensure all keys are lowercase and mapped to fixed columns
        product_data = {re.sub(r'\W+', '_', k.lower()): v for k, v in product_data.items()}

        # Merge product_data with df
        product_data['title'] = title
        product_data['brand'] = brand
        product_data['conditions'] = condition
        product_data['price'] = price

        # Store data in database
        with db_manager.connect() as conn:
            db_manager.create_tables(conn)
            product_id = db_manager.insert_product_data(conn, product_data)
            db_manager.insert_product_images(conn, product_id, image_urls)
            conn.commit()

        print(f"Processed product {i}: {title}.")


if __name__ == '__main__':
    args = parse_args()

    # Read CSV
    try:
        df = pd.read_csv(args.product_list_csv, encoding='latin1')  # Common fallback for non-UTF-8 encodings
    except UnicodeDecodeError:
        # If 'latin1' doesn’t work, try 'ISO-8859-1' or 'cp1252'
        df = pd.read_csv(args.product_list_csv, encoding='ISO-8859-1')

    df.reset_index(inplace=True)

    output_dir_path = args.output_dir_path
    product_category = args.product_category

    # Create directory if it doesn't exist
    os.makedirs(output_dir_path, exist_ok=True)

    # Process and store product data in the database
    process_product_data(df, output_dir_path, product_category)

    print("All detailed pages processed and saved to the database.")
