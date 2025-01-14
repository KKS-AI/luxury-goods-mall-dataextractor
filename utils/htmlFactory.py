from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import random

def format_html(input_html: str) -> str:
    """
    Takes a one-line HTML string and returns it as a formatted, indented HTML string.

    Args:
        input_html (str): A one-line HTML string.

    Returns:
        str: Formatted, indented HTML string.
    """
    soup = BeautifulSoup(input_html, 'html.parser')
    return soup.prettify()


def arrange_html_file(input_html: str, output_file: str) -> None:
    """
    Writes a formatted, indented HTML string to a file.

    Args:
        input_html (str): A one-line HTML string.
        output_file (str): The file to write the formatted HTML to.
    """
    # read the input html file
    with open(input_html, 'r', encoding='utf-8') as f:
        input_html = f.read()
    formatted_html = format_html(input_html)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(formatted_html)

def extract_product_details_from_html(html_content):
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Locate the product grid
    product_elements = soup.select('.plp__products-grid .plp__product')

    # Initialize a list to store product details
    products = []

    # Extract details for each product
    for product in product_elements:
        # Extract product link
        link_element = product.select_one('.plp__card')
        link = link_element['href'] if link_element else "N/A"

        # Extract image URL
        img_element = product.select_one('.products-carousel__card-image')
        img_url = img_element['src'] if img_element else "N/A"

        # Extract title
        title_element = product.select_one('.products-carousel__card-title')
        title = title_element.get_text(strip=True) if title_element else "N/A"

        # Extract designer
        designer_element = product.select_one('.products-carousel__card-designer')
        designer = designer_element.get_text(strip=True) if designer_element else "N/A"

        # Extract condition
        condition_element = product.select_one('.products-carousel__card-condition')
        condition = condition_element.get_text(strip=True) if condition_element else "N/A"

        # Extract price
        price_element = product.select_one('.rewards-plus-plp__product-price-value')
        price = price_element.get_text(strip=True) if price_element else "N/A"

        # Append the extracted details to the products list
        products.append({
            "Link": link,
            "Image URL": img_url,
            "Title": title,
            "Designer": designer,
            "Condition": condition,
            "Price": price
        })

    # Print each product's details
    for i, product in enumerate(products, 1):
        print(f"Product {i}:")
        print(f"  Link: {product['Link']}")
        print(f"  Image URL: {product['Image URL']}")
        print(f"  Title: {product['Title']}")
        print(f"  Designer: {product['Designer']}")
        print(f"  Condition: {product['Condition']}")
        print(f"  Price: {product['Price']}")
        print("-" * 50)

    return products


def download_full_html(url, file_path, target_element=None):
    # Set up Chrome options
    service=Service(executable_path=r"C:\Users\pannython\.cache\selenium\chromedriver\win64\130.0.6723.91\chromedriver.exe")
    options = Options()
    options.headless = True
    # Add user-agent to mimic a real browser
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Initialize the WebDriver with modified options
    driver = webdriver.Chrome(options=options, service=service)

    # Prevent detection of WebDriver (optional)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
        """
    })

    try:
        # Load the URL
        driver.get(url)

        # Wait for the 'Skip to content' link and click it
        try:
            skip_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.skip-to-content'))
            )
            skip_link.click()
            print("Clicked 'Skip to content' link.")
        except Exception as e:
            print("No 'Skip to content' link or failed to click it:", e)

        # Hide the promotional carousel using JavaScript
        try:
            driver.execute_script("var element = document.querySelector('.top-carousel-promo'); if (element) { element.style.display='none'; }")
            print("Promotional carousel hidden.")
        except Exception as e:
            print("Failed to hide promotional carousel:", e)

       # Retry loading target element with exponential backoff
        retry_count = 5  # number of retries
        delay = 10  # initial delay in seconds
        for attempt in range(retry_count):
            try:
                if target_element:
                    WebDriverWait(driver, delay * (attempt + 1)).until(
                        EC.presence_of_element_located((By.CLASS_NAME, target_element))
                    )
                    print("Target element loaded.")
                    break  # Exit loop if element is found
            except Exception as e:
                print(f"Attempt {attempt + 1}: Failed to load target element '{target_element}'. Retrying...")
                time.sleep(2)  # Wait a bit before retrying
        else:
            print(f"Failed to load target element '{target_element}' after {retry_count} attempts.")

        # Get the full HTML content
        full_html = driver.page_source

        # Save the HTML to a file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(full_html)
        print(f"Full HTML content downloaded and saved to {file_path}")

    finally:
        # Close the WebDriver
        driver.quit()



if __name__ == '__main__':
    from config.rebag import global_product_elements_class_name
    # Set the base URL and initialize an empty list to store all products
    base_url = "https://shop.rebag.com/collections/all-watches?page={}"
    all_products = []

    # Loop through the desired number of pages
    for i in range(1, 5):
        url = base_url.format(i)
        file_path = f"rebag-all-watches-mainpage{i}.html"
        download_full_html(url, file_path, global_product_elements_class_name)

        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()

        products = extract_product_details_from_html(html)
        all_products.extend(products)
        print(f"Page {i} done.")

        # Optional: Wait between requests to prevent overloading the server
        time.sleep(2)

    # Create a DataFrame from the extracted products
    df = pd.DataFrame(all_products)

    # Save the DataFrame to a CSV file
    df.to_csv('rebag_products.csv', index=False)

    print("Data extraction complete. Products saved to 'rebag_products.csv'.")

def fix_file_slashes(filepath: str) -> str:
    """
    Converts forward slashes to backslashes in a file path.
    
    Args:
        filepath (str): The original file path
        
    Returns:
        str: Path with forward slashes replaced by backslashes
    """
    return filepath.replace('/', '\\')


def download_detailed_page_full_html(url, file_path, target_element=None):
    # Set up Chrome options
    options = Options()
    options.headless = False  # Run in non-headless mode to reduce detection
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/89.0.4389.82 Safari/537.36"
    )

    # Corrected experimental options
    # You can comment out the next line if it still causes issues
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option("useAutomationExtension", False)

    # Initialize the WebDriver with undetected-chromedriver
    driver = uc.Chrome(options=options)

    # Modify navigator properties to prevent detection
    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    """)

    try:
        # Load the URL
        driver.get(url)
        time.sleep(random.uniform(2, 5))  # Random delay to mimic human behavior
               # Wait for the 'Skip to content' link and click it
        try:
            skip_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.skip-to-content'))
            )
            skip_link.click()
            print("Clicked 'Skip to content' link.")
        except Exception as e:
            print("No 'Skip to content' link or failed to click it:", e)

        # Hide the promotional carousel using JavaScript
        try:
            driver.execute_script("var element = document.querySelector('.top-carousel-promo'); if (element) { element.style.display='none'; }")
            print("Promotional carousel hidden.")
        except Exception as e:
            print("Failed to hide promotional carousel:", e)


            # Check if the URL has changed to an undesired page
        current_url = driver.current_url
        if current_url != url:
            print("Redirected to a different page after closing popup.")
            # Go back to the desired page
            driver.back()
            time.sleep(2)  # Wait for the page to load
            driver.forward()  # Move forward to the redirected page
            time.sleep(2)  # Wait for the page to load
            print("Navigated back to the original page.")

        

        # Mimic user scrolling
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(0, scroll_height, 1000):
            driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(random.uniform(0.5, 1.5))

        # Additional wait to ensure all content loads
        time.sleep(random.uniform(2, 5))

        # Retry loading target element with exponential backoff
        retry_count = 5  # number of retries
        delay = 10  # initial delay in seconds
        for attempt in range(retry_count):
            try:
                if target_element:
                    WebDriverWait(driver, delay * (attempt + 1)).until(
                        EC.presence_of_element_located((By.CLASS_NAME, target_element))
                    )
                    print("Target element loaded.")
                    break  # Exit loop if element is found
            except Exception as e:
                print(f"Attempt {attempt + 1}: Failed to load target element '{target_element}'. Retrying...")
                time.sleep(2)  # Wait a bit before retrying
        else:
            print(f"Failed to load target element '{target_element}' after {retry_count} attempts.")
        
        

        # Get the full HTML content
        full_html = driver.page_source
        # file_path = fix_file_slashes(file_path)
        
     
        # Save the HTML to a file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(full_html)
        print(f"Full HTML content downloaded and saved to {file_path}")

    finally:
        # Close the WebDriver
        driver.quit()