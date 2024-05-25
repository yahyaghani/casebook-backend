from openai import OpenAI
import json 

from src.core.process.helpers_web_parse_cleaner import clean_html, tfidf_extract_keywords, convert_spaces_to_percent20, perform_google_search, perform_google_search_legislation, fetch_and_clean_url_content, smart_parse_action_input
from src.core.prompts.search_prompt import search_sample
from src.db.chroma_model import query_articles, fetch_and_store_content_chromadb
from src.core.agents.tool_wrap import functions
from src.core.agents.main_client import client

known_actions = {
    "performGoogleSearch": perform_google_search,
    "performGoogleSearchLegislation": perform_google_search_legislation,
    "fetchAndStoreContentChromadb": fetch_and_store_content_chromadb,
    "queryArticles": query_articles
}

SYSTEM_MESSAGE = search_sample

MAX_CALLS = 2

def get_openai_response(functions, messages):
    return client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        functions=functions,
        function_call="auto",
        temperature=0.2,
    )

def process_user_instruction(functions, instruction):
    num_calls = 0
    messages = [
        {"content": SYSTEM_MESSAGE, "role": "system"},
        {"content": instruction, "role": "user"},
    ]
    results_summary = []

    while num_calls < MAX_CALLS:
        response = get_openai_response(functions, messages)
        print(response)
        message = response.choices[0].message
        print(message)
        
        if message.function_call:
            function_call = message.function_call
            function_name = function_call.name
            arguments = json.loads(function_call.arguments)

            # Call the function and get the result
            function = known_actions[function_name]
            
            # Ensure the arguments match the expected parameters of the function
            if function_name in ["performGoogleSearchLegislation", "performGoogleSearch"]:
                result = function(arguments["parameters"]["query"], arguments["parameters"].get("page", 1))
            elif function_name == "fetchAndStoreContentChromadb":
                result = function(arguments["requestBody"])
                # After storing content, query for relevant articles
                if "title" in arguments["requestBody"]:
                    query_result = query_articles(arguments["requestBody"]["title"])
                    results_summary.append({
                        "function": "queryArticles",
                        "result": query_result
                    })
            else:
                result = function(**arguments)

            # Summarize the result
            results_summary.append({
                "function": function_name,
                "result": result
            })

            messages.append({
                "role": "function",
                "name": function_name,
                "content": json.dumps(result)
            })
            num_calls += 1
        else:
            print("\n>> Message:\n")
            print(message.content)
            break

    if num_calls >= MAX_CALLS:
        print(f"Reached max chained function calls: {MAX_CALLS}")

    return results_summary

USER_INSTRUCTION = """
Draft a cease and desist letter on behalf of John Doe, whose image was used in a commercial without his permission.

"""

# What is the legislation on AI in the UK?

answer = process_user_instruction(functions, USER_INSTRUCTION)

print('res', answer)
