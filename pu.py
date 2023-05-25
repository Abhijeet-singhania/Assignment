import csv
import requests
from bs4 import BeautifulSoup
import time

# Set the base URL and headers
base_url = "https://www.amazon.in"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
}

# Initialize the CSV file and headers
csv_file = open("amazon_products.csv", "w", newline="", encoding="utf-8")
writer = csv.writer(csv_file)
writer.writerow(["Product URL", "Product Name", "Product Price", "Rating", "Number of Reviews", "Description", "ASIN", "Product Description", "Manufacturer"])

# Function to scrape product details from a product URL
def scrape_product_details(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Scrape required product details
    product_name = soup.select_one("#productTitle").get_text(strip=True)
    product_price = soup.select_one("#priceblock_ourprice").get_text(strip=True)
    rating = soup.select_one(".a-icon-star span").get_text(strip=True)
    num_reviews = soup.select_one("#acrCustomerReviewText").get_text(strip=True)
    description = soup.select_one("#productDescription").get_text(strip=True)
    asin = soup.find("th", text="ASIN").find_next("td").get_text(strip=True)
    product_description = soup.select_one("#feature-bullets ul").get_text(strip=True)
    manufacturer = soup.find("th", text="Manufacturer").find_next("td").get_text(strip=True)

    # Write the data to the CSV file
    writer.writerow([url, product_name, product_price, rating, num_reviews, description, asin, product_description, manufacturer])

# Function to scrape products from a search page
def scrape_products(search_url, num_pages):
    for page in range(1, num_pages + 1):
        url = search_url + f"&page={page}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        # Get the product links from the search page
        product_links = soup.select(".s-result-item .a-link-normal.a-text-normal")
        
        # Iterate over each product link and scrape the details
        for link in product_links:
            product_url = base_url + link["href"]
            scrape_product_details(product_url)
            
        # Add a delay to avoid overwhelming the server
        time.sleep(2)

# Start scraping the products
search_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_"
num_pages = 20  # Scrape 20 pages of product listings

scrape_products(search_url, num_pages)

# Close the CSV file
csv_file.close()

print("Scraping completed and data exported to 'amazon_products.csv'")
