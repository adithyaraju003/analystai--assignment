import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Function to scrape product data from a single listing page
def scrape_product_list_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    products = []

    # Extracting product details
    for product in soup.find_all("div", {"data-asin": True}):
        product_url = f"https://www.amazon.in/dp/{product['data-asin']}"
        
        product_name_tag = product.find("span", class_="a-size-medium")
        product_name = product_name_tag.text.strip() if product_name_tag else None

        product_price_tag = product.find("span", class_="a-offscreen")
        product_price = product_price_tag.text.strip() if product_price_tag else None

        product_rating_tag = product.find("span", class_="a-icon-alt")
        rating = float(product_rating_tag.text.split()[0]) if product_rating_tag else None

        num_reviews_tag = product.find("span", {"class": "a-size-base", "dir": "auto"})
        num_reviews = int(num_reviews_tag.text.replace(",", "")) if num_reviews_tag else None

        products.append({
            "Product URL": product_url,
            "Product Name": product_name,
            "Product Price": product_price,
            "Rating": rating,
            "Number of Reviews": num_reviews
        })

    return products

# Function to scrape product details from a single product page
def scrape_product_details(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Initialize variables to store data
    description = None
    asin = None
    product_desc = None
    manufacturer = None

    # Extracting additional product details
    description_tag = soup.find("meta", {"name": "description"})
    if description_tag:
        description = description_tag.get("content")

    asin_tag = soup.find("input", {"id": "ASIN"})
    if asin_tag:
        asin = asin_tag.get("value")

    product_desc_tag = soup.find("div", {"id": "productDescription"})
    if product_desc_tag:
        product_desc = product_desc_tag.get_text(strip=True)

    manufacturer_tag = soup.find("a", {"id": "bylineInfo"})
    if manufacturer_tag:
        manufacturer = manufacturer_tag.text.strip()

    return {
        "Description": description,
        "ASIN": asin,
        "Product Description": product_desc,
        "Manufacturer": manufacturer
    }

# Main function to scrape data from multiple pages and export to CSV
def main():
    product_data = []
    for page_number in range(1, 21):
        url = f"https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{page_number}"
        page_data = scrape_product_list_page(url)
        product_data.extend(page_data)
        time.sleep(2)  # Add a small delay to avoid overwhelming the server

    # Fetch additional details for each product URL
    for product in product_data:
        product_details = scrape_product_details(product['Product URL'])
        product.update(product_details)
        time.sleep(1)  # Add a small delay to avoid overwhelming the server

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(product_data)

    # Export the DataFrame to CSV
    df.to_csv("amazon_products.csv", index=False)

    print("Data scraping and CSV export completed successfully.")

if __name__ == "__main__":
    main()
