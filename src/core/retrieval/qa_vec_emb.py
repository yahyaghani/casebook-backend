import json
from langchain_community.document_loaders import JSONLoader
from pathlib import Path
from pprint import pprint
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
from langchain.chains import create_qa_with_sources_chain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os 

def load_highlights(file_path):
    # Load the JSON file into a dictionary
    data = json.loads(Path(file_path).read_text())

    # Initialize the JSONLoader with custom parsing logic
    loader = JSONLoader(
        file_path=file_path,
        # jq_schema='.highlights[].content.text',  # Navigate to each content's text
        jq_schema='.text_body',  # Navigate to each content's text

        text_content=True,  # We are directly using text content
        metadata_func=metadata_func  # Optional: Define if metadata needs to be captured
    )

    # Load the data using the configured loader
    documents = loader.load()
    return documents
    # Print the loaded documents
    # pprint(documents)

# Define a metadata function to assign sequence numbers and handle additional metadata
def metadata_func(record, metadata):
    # Increment seq_num based on the number of documents processed
    metadata['seq_num'] = metadata.get('seq_num', 0) + 1
    # Optional: Include other metadata if required
    return metadata

# Example JSON file path
file_path = '/home/taymur/Documents/legal2/DATA/Highlight/newmerged/CASEEBACKk_v2/src/static/notes/9c758549-40b8-401a-bfa2-9a304d71ec74/Williams.APPROVED-JUDGMENTS.pdf.json'

# Load and print the highlights as documents
documents=load_highlights(file_path)


# Setup Text Splitter and Split Documents
text_splitter = CharacterTextSplitter(chunk_size=1550, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# Embeddings and Document Search
api_key = os.getenv("OPENAI_API_KEY", "fallback_api_key_if_none_found")
embeddings = OpenAIEmbeddings(api_key=api_key)
docsearch = Chroma.from_documents(texts, embeddings)

# Setup the Question Answering Chain
llm = ChatOpenAI(api_key=api_key, model="gpt-3.5-turbo-1106")
qa_chain = create_qa_with_sources_chain(llm)
doc_prompt = PromptTemplate(
    template="Content: {page_content}\nSource: {source}",
    input_variables=["page_content", "source"],
)

final_qa_chain = StuffDocumentsChain(
    llm_chain=qa_chain,
    document_variable_name="context",
    document_prompt=doc_prompt,
)

retrieval_qa = RetrievalQA(
    retriever=docsearch.as_retriever(), combine_documents_chain=final_qa_chain
)

# query = "What are the legal tests presented to us"
query = "What are the key facts presented to us"


answer = retrieval_qa.run(query)
print(answer)
