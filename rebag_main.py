

import os
import sys
import shutil
import re
from config.rebag import global_product_elements_class_name, each_product_details_elements_class_name
from utils.htmlFactory import download_full_html, extract_product_details_from_html, download_detailed_page_full_html
from utils.parserFactory import RebagProductScraper, scrape
from utils.dbFactory import DatabaseManager
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor

def clear_temp_folder(path=r"C:\Users\pannython\AppData\Local\Temp"):
    # Check if the directory exists
    if not os.path.exists(path):
        print(f"The directory {path} does not exist.")
        return

    # Iterate through files and directories in the specified path
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        
        try:
            # Remove files
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
                print(f"Deleted file: {item_path}")
            
            # Remove directories
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Deleted folder: {item_path}")
        
        except Exception as e:
            print(f"Could not delete {item_path}. Reason: {e}")

    print("Temp folder cleared.")


def download_page(i):
    url = df['Link'][i]
    title = df['Title'][i].replace('/', '_')  # replace '/' in title
    brand = df['Designer'][i]
    condition = df['Condition'][i]
    price = df['Price'][i]
    file_path = os.path.join(output_dir_path, f"index_{i}_{title}_{brand}_{condition}_{price}.html")
    download_detailed_page_full_html(url, file_path, each_product_details_elements_class_name)
    print(f"Downloaded detailed page: {file_path}")
    clear_temp_folder()
    print("Temp folder cleared.")
    return file_path


if __name__ == '__main__':
    #############################################
    ## Fisrt Step: Download all the main pages ##
    #############################################
    product_category = 'bags'
    all_page_downloaded = True
    file_name = f'{product_category}_rebag_products.csv'


    # if os.path.exists(file_name):
    #     all_page_downloaded = True
    #     # df_origin = pd.read_csv(file_name)

    # if all_page_downloaded:
    #     print("All pages are already downloaded.")

    # else:
    #     # Set the base URL and initialize an empty list to store all products
    #     # all_products = []

    #     # Loop through the desired number of pages
    #     # first 1 ~200
    #     # second 201 ~ 483
    #     for i in range(201, 483):
    #         all_products = []
            

    #         base_url = f'https://shop.rebag.com/collections/all-{product_category}?page={i}'
    #         url = base_url
    #         file_path = f"rebag-all-{product_category}-mainpage{i}.html"
    #         download_full_html(url, file_path, global_product_elements_class_name)

    #         with open(file_path, 'r', encoding='utf-8') as f:
    #             html = f.read()

    #         products = extract_product_details_from_html(html)
    #         all_products.extend(products)
            

    #         # Optional: Wait between requests to prevent overloading the server
    #         time.sleep(2)
    #         df = pd.DataFrame(all_products)
    #         df.to_csv(file_name, mode='a', header=False, index=False)
    #         print(f"Page {i} done.")
    #         os.remove(file_path)

        # # Create a DataFrame from the extracted products
        # df = pd.DataFrame(all_products)

        # # Save the DataFrame to a CSV file
        # df.to_csv(file_name, index=False)

        #  print(f"Data extraction complete. Products saved to {file_name}.")


    #################################################
    ## Second Step: Get detailed information to db ##
    # #################################################
    csvfile = r'E:\kangkas\데이터 라벨링 구축사업\src\main\luxury-goods-mall-dataextractor\bags_rebag_products.csv'
 
    try:
        df = pd.read_csv(csvfile, encoding='latin1')  # Common fallback for non-UTF-8 encodings
    except UnicodeDecodeError:
        # If 'latin1' doesn’t work, try 'ISO-8859-1' or 'cp1252'
        df = pd.read_csv(csvfile, encoding='ISO-8859-1')
    # df = df
    df.reset_index(inplace=True)
    output_dir_path = r'E:\kangkas\데이터 라벨링 구축사업\src\main\luxury-goods-mall-dataextractor\product_html\bags'

    for i in range(954, len(df)):
        url = df['Link'][i]
        title = df['Title'][i]
        brand = df['Designer'][i]
        condition = df['Condition'][i]
        price = df['Price'][i]

        # product = 'wathces'
        # if '/' in title:
        #     title = title.replace('/', '_')


        file_path = os.path.join(output_dir_path, f"index_{i}_{title}_{brand}_{condition}_{price}.html")
        # download_detailed_page_full_html(url, file_path, each_product_details_elements_class_name)
        # print("Downloaded detailed page: file_path {}".format(file_path))


        # # Parse the HTML content
        # parser = RebagProductScraper(html, file_path)
        db_manager = DatabaseManager()

        # Extract product details
        product_data, image_urls = scrape(file_path)

        # Ensure all keys are lowercase and mapped to fixed columns
        product_data = {re.sub(r'\W+', '_', k.lower()): v for k, v in product_data.items()}

        # merge product_data with df
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

    #     print("Data and images inserted successfully.")
    #     os.remove(file_path)
    #     print("Removed file: {}".format(file_path))
    #  Use ThreadPoolExecutor to parallelize the downloads
    # with ThreadPoolExecutor(max_workers=5) as executor:
    #     executor.map(download_page, range(13207, len(df)))

    print("All detailed pages processed and saved to database.")



        