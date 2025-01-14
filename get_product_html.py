import os
import pandas as pd
import shutil
import argparse
from config.rebag import each_product_details_elements_class_name
from utils.htmlFactory import download_detailed_page_full_html
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


def download_page(i, df, output_dir_path):
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


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Download detailed pages from a CSV of product links.')
    parser.add_argument('--csvfile', type=str, help='Path to the CSV file with product list data', required=True)
    parser.add_argument('--output_dir_path', type=str, help='Directory to save downloaded HTML files', required=True)
    parser.add_argument('--start_row', type=int, help='Row to start processing from', default=0)
    parser.add_argument('--end_row', type=int, help='Row to stop processing at', default=None)
    parser.add_argument('--workers', type=int, help='Number of workers to use for parallel processing', default=5)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    # Read CSV
    try:
        df = pd.read_csv(args.csvfile, encoding='latin1')  # Common fallback for non-UTF-8 encodings
    except UnicodeDecodeError:
        # If 'latin1' doesn’t work, try 'ISO-8859-1' or 'cp1252'
        df = pd.read_csv(args.csvfile, encoding='ISO-8859-1')
    
    df.reset_index(inplace=True)
    
    # Set output directory from args
    output_dir_path = args.output_dir_path

    # Set the range of rows to process from arguments, if specified
    start_row = args.start_row
    end_row = args.end_row if args.end_row else len(df)

    # Use ThreadPoolExecutor to parallelize the downloads
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        executor.map(lambda i: download_page(i, df, output_dir_path), range(start_row, end_row))

    print("All detailed pages processed and saved.")
