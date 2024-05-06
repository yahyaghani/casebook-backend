import os
from langchain.chains import create_citation_fuzzy_match_chain
from langchain_openai import ChatOpenAI
import json 

# Setup the Language Model with OpenAI
def setup_language_model():
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-1106", openai_api_key=openai_api_key)
    return llm

# Create a chain for citation fuzzy match
def setup_citation_chain(llm):
    return create_citation_fuzzy_match_chain(llm)

def get_highlights(highlights):
    results = []
    for highlight in highlights:
        comment_text = highlight['comment']['text']  # Access the text inside comment
        content_text = highlight['content']['text']  # Access the text inside content
        results.append((comment_text, content_text))
    return results


# Function to highlight text based on spans
def highlight(text, span):
    start = max(span[0] - 20, 0)  # Adjusted to handle edge case where span[0] < 20
    end = min(span[1] + 20, len(text))  # Adjusted to handle edge case where span[1] + 20 exceeds text length
    return "..." + text[start:span[0]] + "*" + "\033[91m" + text[span[0]:span[1]] + "\033[0m" + "*" + text[span[1]:end] + "..."



# Run the citation extraction
def get_citations(question, context):
    llm = setup_language_model()
    chain = setup_citation_chain(llm)
    input_data = {
        "question": question,
        "context": context
    }

    try:
        # result = chain.invoke(question=question, context=context)
        result = chain.invoke(input=input_data)
        print('Result received:', result['text'])
        # # # Manually extract data to ensure it is serializable
        # serialized_result = {
        #     "question": question,
        #     "answers": [
        #         {
        #             "fact": result['text'],
        #             "quotes": fact["substring_quote"]
        #         } for fact in result["text"]["answer"]  # Correcting how we access the 'answer' field
        #     ]
        # }
        # return serialized_result['text']
        return result['text']
        # print('qA',serialized_result)
        # Serialize the manually constructed dictionary to a JSON string
        # result_json = json.dumps(serialized_result, ensure_ascii=False, indent=4)
        
        # # Save the JSON to a file
        # with open("result.json", "w", encoding="utf-8") as file:
        #     file.write(result_json)
        # print("Result saved as JSON.")
        
    except Exception as e:
        print(f"Error invoking chain or saving JSON: {e}")
        return []

    # output = []
    
    # # Assuming result['text']['answer'] is accessible and structured as expected
    # if 'text' in result:
    #     answers = result['text']['answer']
    #     for fact in answers:
    #         print("Processing statement:", fact['fact'])
    #         try:
    #             for quote in fact['substring_quote']:
    #                 start = context.index(quote)
    #                 end = start + len(quote)
    #                 print(f"Processing span: {start}, {end}")
    #                 citation_text = highlight(context, (start, end))
    #                 output.append((fact['fact'], citation_text))
    #         except Exception as e:
    #             print(f"Error processing spans for fact '{fact['fact']}': {e}")
    # else:
    #     print("No answer returned from chain or missing expected data structure.")
    
    # return output

# Load context from JSON
def load_context_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data.get('highlights', [])  # Directly return the highlights list
    except Exception as e:
        print(f"An error occurred: {e}")
        return []  # Return an empty list on error


# # Main execution flow
file_path = '../../static/highlights/9c758549-40b8-401a-bfa2-9a304d71ec74/Williams.APPROVED-JUDGMENTS.pdf.json'
json_data = load_context_from_json(file_path)
highlight_pairs = get_highlights(json_data)
highlighted_context = " ".join([content for _, content in highlight_pairs])

# print("Combined Context:")
# print(highlighted_context)  # This prints the combined context from all highlight pairs

# Now use this combined context to get citations
question = "What are the legal tests presented to us"
citations = get_citations(question, highlighted_context)
for citation in citations:
    print(f"Citation: {citation}\n")
# Extracting each FactWithEvidence element into a list of dictionaries
# Extracting each FactWithEvidence element into a list of dictionaries
fact_with_evidence_list = []

for citation_type, citation_data in citations:
    if citation_type == 'answer':
        for fact_with_evidence in citation_data:
            fact_with_evidence_dict = {
                'fact': fact_with_evidence.fact,
                'substring_quote': fact_with_evidence.substring_quote
            }
            fact_with_evidence_list.append(fact_with_evidence_dict)

# Printing the list of dictionaries
print(fact_with_evidence_list)
