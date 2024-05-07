from bs4 import BeautifulSoup
import httpx
from urllib.parse import quote

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    clean_text = soup.get_text()
    # Optionally, you can also remove references or other unwanted parts here
    return clean_text

from sklearn.feature_extraction.text import TfidfVectorizer

def convert_spaces_to_percent20(text):
    # The `safe` parameter determines which characters should not be quoted. Here, we are encoding everything except the alphanumeric characters.
    return quote(text, safe='')

def tfidf_extract_keywords(query):
    # Initialize a TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')

    # Assume each word in the query is a separate document for simplicity
    words = query.split()
    # Fit and transform the 'documents'
    tfidf_matrix = vectorizer.fit_transform(words)

    # Get feature names to use as output
    feature_names = vectorizer.get_feature_names_out()

    # Sort words by their TF-IDF scores
    sorted_items = sorted(zip(vectorizer.idf_, feature_names), reverse=True)

    # Extract top 3 keywords
    top_keywords = [item[1] for item in sorted_items[:3]]
    return ", ".join(top_keywords)
