from bs4 import BeautifulSoup
import httpx
from urllib.parse import quote
import os 
import requests
import re
from pdfminer.high_level import extract_text

# Set up the environment variables (for testing purposes, set them directly)
# os.environ['GOOGLE_API_KEY'] = 'your_google_api_key_here'  # Replace with your actual Google API key

my_api_key = os.getenv('GOOGLE_API_KEY')
my_cse_id= '754370c1b456c454f'

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    clean_text = soup.get_text()
    # Optionally, you can also remove references or other unwanted parts here
    return clean_text

from sklearn.feature_extraction.text import TfidfVectorizer

def convert_spaces_to_percent20(text):
    return quote(text, safe='')

def perform_google_search_legislation(query: str, page: int = 1):
    """
    Performs a Google Custom Search and prints the results.

    Args:
    query (str): The search query.
    page (int): The page number of the search results to retrieve.

    Returns:
    dict: The search results.
    """
    # Retrieve API key and search engine ID from environment variables
    API_KEY = os.getenv('GOOGLE_API_KEY')
    SEARCH_ENGINE_ID = '754370c1b456c454f'

    # Calculate the start index for the results on the specified page
    start = (page - 1) * 3 + 1

    # Construct the API request URL
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}&start={start}&num=3"

    # Make the API request
    response = requests.get(url)
    print(response)
    if response.status_code != 200:
        print(f"Failed to fetch data: HTTP {response.status_code}")
        return
    
    # Parse the JSON response
    data = response.json()

    # Get the result items
    search_items = data.get("items")
    if not search_items:
        print("No results found.")
        return
    results = []

    # Iterate over the results found
    for i, search_item in enumerate(search_items, start=1):
        # Extract data from each result
        result_dict = {
            "result_number": i + start - 1,
            "title": search_item.get("title"),
            "description": search_item.get("snippet"),
            "long_description": search_item.get("pagemap", {}).get("metatags", [{}])[0].get("og:description", "N/A"),
            "url": search_item.get("link")
        }
        results.append(result_dict)

    return {"results": results}

# Test the perform_google_search_legislation function
def test_perform_google_search_legislation():
    query = "What is the legislation on AI in the UK?"
    page = 1

    results = perform_google_search_legislation(query, page)

    if results:
        for result in results["results"]:
            print(f"Result #{result['result_number']}")
            print(f"Title: {result['title']}")
            print(f"Description: {result['description']}")
            print(f"Long Description: {result['long_description']}")
            print(f"URL: {result['url']}")
            print()

# Call the test function
test_perform_google_search_legislation()
