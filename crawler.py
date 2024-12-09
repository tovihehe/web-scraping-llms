
from bs4 import BeautifulSoup
import requests
import os
from scrapingbee import ScrapingBeeClient
from dotenv import load_dotenv
import json

# Load env 
load_dotenv('.env', override=True)

def extract_events(client, url, type):
    """
    Extracts the events from the specified URL and returns a list of related websites.
    """
    try:

        print(f"Extracting html data from: {url}")
        # Attempt to get the content from the URL.
        response = client.get(
                            url,
                            params={
                                # Use premium proxies for tough sites
                                'premium_proxy': True,  
                                'country_code': 'es',
                                # Block images and CSS to speed up loading
                                "block_resources": True, 
                                'device': 'desktop',
                            }
                        )
        # Get the HTML content of the response.
        html_response = response.content

        # Parse the HTML content of the response.
        soup = BeautifulSoup(html_response, "html.parser")

        # Find the specific section by its ID
        if type == "exposiciones":
            specific_section = soup.find(id="portlet_listactivities_INSTANCE_u3YZVHkpD017")
        elif type == "actividades":
            specific_section = soup.find(id="portlet_listactivities_INSTANCE_Q4EA43110XIZ")
        elif type == "planetario":
            specific_section = soup.find(id="portlet_listactivities_INSTANCE_n4imOHR5Ia1i")
        elif type == "conferencias":
            specific_section = soup.find(id="portlet_listactivities_INSTANCE_WvGPDs7XuZX8")

        # Initialize a list to store related websites
        list_related_websites = []

        # Check if the specific section exists
        if specific_section:
            # Extract links only from the specific section
            for link in specific_section.find_all("a", href=True):
                href = link.get("href")
                if href.startswith("https://cosmocaixa.org/es/p/"):
                    list_related_websites.append(href)

        # Now list_related_websites contains URLs from the specified section
        return list(set(list_related_websites))

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

# Define the sources of the data
sources = {
    "exposiciones": "https://cosmocaixa.org/es/exposiciones-ciencia-barcelona",
    "actividades": "https://cosmocaixa.org/es/actividades-cosmocaixa-ciencia",
    "planetario": "https://cosmocaixa.org/es/planetario",
    "conferencias": "https://cosmocaixa.org/es/conferencias"
}

# Initialize the ScrapingBee client with the API key
client = ScrapingBeeClient(api_key=os.getenv("SCRAPINGBEE_API_KEY"))

# Create a JSON with the urls of each type: exposiciones, actividades, planetario, conferencias
urls = {}
for type, source in sources.items():
    urls[type] = extract_events(client, source, type)

# Print the URLs for each type
for type, url in urls.items():
    print(f"URLs for {type}: {url}")

# Save the URLs to a JSON file
with open('urls.json', 'w') as f:
    json.dump(urls, f)