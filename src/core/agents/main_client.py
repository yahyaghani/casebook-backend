
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

# key="sk-proj-4DIV8YjEXmqv4K9riEHcT3BlbkFJj8QzejVqiWQlAz6ZqtFM"
client = OpenAI(api_key=api_key)
