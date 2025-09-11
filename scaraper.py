from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from webdriver_manager.firefox import GeckoDriverManager
import pandas as pd
import time
import random
import json

# Define a list of User-Agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/119.0",
]

# Update with your actual Firefox profile path
profile_path = "/home/your-name/.mozilla/firefox/abcdefgh.your-profile"

# Setup Firefox options for stealth mode
options = Options()
options.profile = FirefoxProfile(profile_path)
options.add_argument("--headless")  # Run in background (no GUI)
options.add_argument("--disable-gpu")
options.set_preference("dom.webdriver.enabled", False)
options.set_preference("useAutomationExtension", False)

# Randomly select a User-Agent
user_agent = random.choice(USER_AGENTS)
options.set_preference("general.useragent.override", user_agent)

# Use WebDriver Manager to install Geckodriver
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

# Redfin search URL for Hollywood Hills, Los Angeles
base_url = "https://www.redfin.com/neighborhood/547223/CA/Los-Angeles/Hollywood-Hills"

# Initialize data storage
scraped_data = []

# Start scraping
driver.get(base_url)
time.sleep(random.uniform(5, 8))  # Random delay

# Check if we are being blocked
print(f"Page title: {driver.title}")
if "Access" in driver.title or "blocked" in driver.page_source.lower():
    print("WARNING: Redfin has blocked the request!")
    driver.quit()
    exit()

page_number = 1
while True:
    print(f"Scraping page {page_number}...")

    # Locate the main listings container
    try:
        container = driver.find_element("css selector", "div.HomeCardsContainer")
        listings = container.find_elements("css selector", "div.HomeCardContainer")
    except:
        print("Failed to locate the property list container. Exiting...")
        break

    print(f"Found {len(listings)} listings on page {page_number}")

    for listing in listings:
        # Extract price
        try:
            price = listing.find_element("css selector", "span.bp-Homecard__Price--value").text.strip()
        except:
            price = "N/A"

        # Extract address
        try:
            address = listing.find_element("css selector", "div.bp-Homecard__Address").text.strip()
        except:
            print("Skipping a listing due to missing address data")
            continue  # Skip listings with missing elements

        # Extract beds, baths, and sqft
        try:
            beds = listing.find_element("css selector", "span.bp-Homecard__Stats--beds").text.strip()
        except:
            beds = "N/A"

        try:
            baths = listing.find_element("css selector", "span.bp-Homecard__Stats--baths").text.strip()
        except:
            baths = "N/A"

        try:
            sqft = listing.find_element("css selector", "span.bp-Homecard__LockedStat--value").text.strip()
        except:
            sqft = "N/A"

        # Extract listing link
        try:
            link = listing.find_element("css selector", "a.link-and-anchor").get_attribute("href")
            link = f"https://www.redfin.com{link}" if link.startswith("/") else link
        except:
            print("Skipping a listing due to missing link data")
            continue  # Skip listings with missing elements

        # Extract image URL
        try:
            image_element = listing.find_element("css selector", "img.bp-Homecard__Photo--image")
            image_url = image_element.get_attribute("src")
        except:
            image_url = "N/A"
        
        try:
            # Extract Geo-Coordinates (Latitude & Longitude)
            json_script = listing.find_element("css selector", "script[type='application/ld+json']").get_attribute("innerHTML")
            json_data = json.loads(json_script)

            latitude = json_data[0]["geo"]["latitude"]
            longitude = json_data[0]["geo"]["longitude"]
        except:
            latitude = "N/A"
            longitude = "N/A"

        # Store the data
        scraped_data.append({
            "Price": price,
            "Address": address,
            "Beds": beds,
            "Baths": baths,
            "SqFt": sqft,
            "Link": link,
            "Image URL": image_url, 
            "Latitude": latitude,
            "Longitude": longitude
        })

    # Pagination: Check if a "Next Page" button exists
    try:
        next_button = driver.find_element("css selector", "button.PageArrow__direction--next")
        next_button.click()
        page_number += 1
        time.sleep(random.uniform(5, 10))  # Random delay before next request
    except:
        print("No more pages. Scraping complete.")
        break  # Exit loop when no next page exists

# Convert to DataFrame and save as CSV
df = pd.DataFrame(scraped_data)
df.to_csv("data/redfin_hollywood_hills.csv", index=False)
print(f"Scraping complete! {len(df)} listings saved to data/redfin_hollywood_hills.csv")

# Close the browser
driver.quit()