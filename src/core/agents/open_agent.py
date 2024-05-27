from openai import OpenAI
import json 
from pydantic import ValidationError, BaseModel
from typing import Any, Dict

from src.core.process.helpers_web_parse_cleaner import (
    clean_html,
    tfidf_extract_keywords,
    convert_spaces_to_percent20,
    perform_google_search,
    perform_google_search_legislation,
    fetch_and_clean_url_content,
    smart_parse_action_input,
    parse_structure
)
from src.core.prompts.search_prompt import search_sample
from src.db.chroma_model import query_articles, fetch_and_store_content_chromadb
from src.core.agents.tool_wrap import functions
from src.core.agents.main_client import client
from src.socketio_instance import socketio_instance
from src.core.process.pydantic_models import (GoogleSearchArguments, GoogleSearchResults, GoogleSearchResultItem,
                                              extract_relevant_keys, ChromadbArguments, ChromadbResult, EmitData)

known_actions = {
    "performGoogleSearch": perform_google_search,
    "performGoogleSearchLegislation": perform_google_search_legislation,
    "fetchAndStoreContentChromadb": fetch_and_store_content_chromadb,
    "queryArticles": query_articles
}

SYSTEM_MESSAGE = search_sample
MAX_CALLS = 2

def get_openai_response(functions, messages):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        functions=functions,
        function_call="auto",
        temperature=0.2,
    )
    print(f"OpenAI response: {response}")  # Debugging statement
    return response

def emit_func(event_type, data):
    # Validate data with Pydantic
    try:
        emit_data = EmitData(**data)
    except ValidationError as ve:
        print(f"EmitData validation error: {ve}")
        emit_data = EmitData(result=data.get('result', ''), error=data.get('error', ''), function=data.get('function', ''))

    # Replace this with your actual emit function to send data to the frontend
    if event_type == 'completion_check':
        message = emit_data.result  # For completion check, we send the data directly as a message
    elif event_type == 'error':
        message = emit_data.error
    else:
        message = emit_data.result

    socketio_instance.emit('openai-query-response', {'recommendation': message})  # Emit only the text after 'Answer:'

    print(f"Emitting {event_type}: {data}")

def process_user_instruction(instruction):
    print("\n--- Starting process_user_instruction ---\n")
    
    messages = [
        {"content": SYSTEM_MESSAGE, "role": "system"},
        {"content": instruction, "role": "user"},
    ]
    results_summary = []
    previous_results = []

    for call_number in range(MAX_CALLS):
        print(f"\n--- Call number {call_number + 1} ---\n")

        response = get_openai_response(functions, messages)
        print(f"\nResponse from OpenAI:\n{response}\n")

        response_message = response.choices[0].message
        print(f"Response message: {response_message}\n")

        if response_message.function_call:
            function_name = response_message.function_call.name
            function_arguments = response_message.function_call.arguments

            print(f"Function call detected: {function_name}\n")
            print(f"Function arguments: {function_arguments}\n")

            try:
                function_arguments = json.loads(function_arguments)
                print(f"Parsed function arguments: {function_arguments}\n")
            except json.JSONDecodeError as e:
                print(f"Failed to parse function arguments: {str(e)}\n")
                emit_func('error', {"error": f"Failed to parse function arguments: {str(e)}", "function": function_name})
                break

            if function_name in known_actions:
                action_function = known_actions[function_name]
                print(f"Known action function: {action_function}\n")

                try:
                    # Map function names to their corresponding argument models
                    model_mapping = {
                        "performGoogleSearch": GoogleSearchArguments,
                        "performGoogleSearchLegislation": GoogleSearchArguments,
                        "fetchAndStoreContentChromadb": ChromadbArguments,
                        "queryArticles": ChromadbArguments
                    }

                    if function_name in model_mapping:
                        argument_model = model_mapping[function_name]
                    else:
                        raise ValueError(f"Model class for function '{function_name}' not found")

                    # Flatten nested 'parameters' if exists
                    if 'parameters' in function_arguments:
                        function_arguments = function_arguments['parameters']

                    function_arguments = extract_relevant_keys(function_arguments, argument_model)

                    # Add original instruction to function arguments if needed
                    if function_name == "fetchAndStoreContentChromadb":
                        function_arguments["instruction"] = instruction

                    # Instantiate the model based on the function
                    arguments_model = argument_model(**function_arguments)

                    # Call the function with arguments
                    if function_name == "fetchAndStoreContentChromadb":
                        action_result = action_function(arguments_model, instruction)
                    else:
                        action_result = action_function(arguments_model)
                    
                    print(f"Action result: {action_result}\n")
                    previous_results.append(action_result)
                    messages.append({"content": str(action_result), "role": "assistant"})
                except ValidationError as ve:
                    print(f"ValidationError encountered: {str(ve)}\n")
                    corrected_arguments = parse_structure(function_name, function_arguments, str(ve))
                    print(f"Corrected arguments: {corrected_arguments}\n")

                    if not corrected_arguments or 'requestBody' not in corrected_arguments or not corrected_arguments['requestBody']:
                        print("Failed to correct the structure of the data or missing required fields.\n")
                        emit_func('error', {"error": "Failed to correct the structure of the data or missing required fields.", "function": function_name})
                        break

                    try:
                        arguments_model = argument_model(**corrected_arguments)
                        if function_name == "fetchAndStoreContentChromadb":
                            action_result = action_function(arguments_model, instruction)
                        else:
                            action_result = action_function(arguments_model)
                        print(f"Action result after correction: {action_result}\n")
                        previous_results.append(action_result)
                        messages.append({"content": str(action_result), "role": "assistant"})
                    except Exception as e:
                        print(f"Function call failed after correction: {str(e)}\n")
                        emit_func('error', {"error": f"Function call failed: {str(e)}", "function": function_name})
                        break
                except Exception as e:
                    print(f"Function call failed: {str(e)}\n")
                    emit_func('error', {"error": f"Function call failed: {str(e)}", "function": function_name})
                    break
            else:
                print(f"Unknown function: {function_name}\n")
                emit_func('error', {"error": f"Unknown function: {function_name}", "function": function_name})
                break
        else:
            print(f"Completion check result: {response_message.content}\n")
            emit_func('completion_check', {"result": response_message.content, "function": function_name})
            results_summary.append(response_message.content)
            break

    print("\n--- Ending process_user_instruction ---\n")
    return results_summary, messages

# Create a function to handle incoming user instructions
def handle_user_instruction(instruction):
    try:
        results = process_user_instruction(instruction)
        emit_func('completion_check', {"result": "\n".join(results), "function": "process_user_instruction"})
    except Exception as e:
        emit_func('error', {"error": f"An error occurred: {str(e)}", "function": "process_user_instruction"})
