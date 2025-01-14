import sqlite3
import re


class DatabaseManager:
    def __init__(self, db_name='product_data.db'):
        self.db_name = db_name
        # Mapping for category-specific columns
        self.category_columns = {
            'watches': [
                "title", "brand", "conditions", "price", "condition_details", "case_size_width",
                "watch_height", "band_width", "wrist_circumference", "dial_color",
                "band_color", "band_material", "case_material", "bezel_material", "movement", "crystal",
                "production_year", "complications", "water_resistance", "certificate_papers", "accessories",
                "store_location", "estimated_retail", "serial_number", "reference_number", "clair_code"
            ],
            'bags': [
                "title", "brand", "conditions", "price", "material", "color", "dimensions", "strap_length",
                "handle_type", "lining", "hardware", "closure_type", "country_of_origin", "serial_number"
            ]
            # Add more categories here as necessary
        }

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self, conn, category):
        cursor = conn.cursor()
        
        # Check if the category exists in the columns mapping
        if category not in self.category_columns:
            raise ValueError(f"Category {category} is not supported.")

        columns_def = ', '.join([f'"{col}" TEXT' for col in self.category_columns[category]])
        create_product_table_query = f'CREATE TABLE IF NOT EXISTS rebag_{category} ({columns_def})'
        cursor.execute(create_product_table_query)
        
        # Create images table
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS rebag_{category}_images (
            product_id INTEGER,
            image_url TEXT,
            FOREIGN KEY(product_id) REFERENCES rebag_{category}(rowid)
        )
        ''')

    def insert_product_data(self, conn, category, product_data):
        cursor = conn.cursor()
        
        # Ensure data matches category-specific columns, filling missing columns with None
        if category not in self.category_columns:
            raise ValueError(f"Category {category} is not supported.")
        
        cleaned_data = {col: product_data.get(col, None) for col in self.category_columns[category]}
        
        # Insert product data
        column_names = ', '.join([f'"{col}"' for col in cleaned_data.keys()])
        placeholders = ', '.join(['?'] * len(cleaned_data))
        insert_query = f'INSERT INTO rebag_{category} ({column_names}) VALUES ({placeholders})'
        cursor.execute(insert_query, list(cleaned_data.values()))
        
        return cursor.lastrowid

    def insert_product_images(self, conn, category, product_id, image_urls):
        cursor = conn.cursor()
        for url in image_urls:
            cursor.execute(
                f'INSERT INTO rebag_{category}_images (product_id, image_url) VALUES (?, ?)', 
                (product_id, url)
            )


# Example Usage
if __name__ == "__main__":
    db_manager = DatabaseManager()

    # Connect to the database
    with db_manager.connect() as conn:
        # Assume category is dynamically determined, here it is 'watches'
        category = 'watches'
        
        # Create tables for the category
        db_manager.create_tables(conn, category)

        # Example product data (this would come from your scraping logic)
        product_data = {
            "title": "Luxury Watch",
            "brand": "Brand X",
            "conditions": "New",
            "price": "1000 USD",
            "condition_details": "No scratches",
            "case_size_width": "40mm",
            "watch_height": "10mm",
            "band_width": "20mm",
            "wrist_circumference": "18cm",
            "dial_color": "Black",
            "band_color": "Black",
            "band_material": "Leather",
            "case_material": "Stainless Steel",
            "bezel_material": "Ceramic",
            "movement": "Automatic",
            "crystal": "Sapphire",
            "production_year": "2022",
            "complications": "Date",
            "water_resistance": "100m",
            "certificate_papers": "Included",
            "accessories": "Box",
            "store_location": "NYC",
            "estimated_retail": "1200 USD",
            "serial_number": "12345ABC",
            "reference_number": "XYZ123",
            "clair_code": "CL123"
        }

        # Insert product data
        product_id = db_manager.insert_product_data(conn, category, product_data)

        # Example images (these would come from your scraping logic)
        image_urls = ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
        
        # Insert product images
        db_manager.insert_product_images(conn, category, product_id, image_urls)

    print("Product data and images inserted successfully.")
