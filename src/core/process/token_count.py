import tiktoken

def get_encoding_for_model(model_name: str):
    """ Retrieve the encoding for a given model. """
    return tiktoken.encoding_for_model(model_name)

def num_tokens_from_string(text: str, encoding_name: str) -> int:
    """ Returns the number of tokens in a text string using a specific encoding. """
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))

def compare_encodings(example_string: str):
    """ Prints a comparison of three string encodings. """
    print(f'\nExample string: "{example_string}"\n')
    for encoding_name in ["r50k_base", "p50k_base", "cl100k_base"]:
        encoding = tiktoken.get_encoding(encoding_name)
        token_integers = encoding.encode(example_string)
        num_tokens = len(token_integers)
        token_bytes = [encoding.decode_single_token_bytes(token) for token in token_integers]

        print(f"{encoding_name}: {num_tokens} tokens")
        print(f"Token integers: {token_integers}")
        print(f"Token bytes: {token_bytes}\n")

def decode_tokens(token_list, encoding_name: str):
    """ Converts a list of token integers back to a string using the specified encoding. """
    encoding = tiktoken.get_encoding(encoding_name)
    return encoding.decode(token_list)

def call_token_count(text, max_tokens):
    # Sample text and model
    model_name = "gpt-3.5-turbo-1106"
    # Retrieve encoding for the model
    encoding = get_encoding_for_model(model_name)
    
    # Tokenize the text and count tokens
    num_tokens = num_tokens_from_string(text, encoding.name)
    print(f'Number of tokens in "{text}": {num_tokens}')
    
    # Check if the number of tokens is within the allowable limit
    return num_tokens <= max_tokens
