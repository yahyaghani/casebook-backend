from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class GoogleSearchArguments(BaseModel):
    query: str
    page: Optional[int] = 1

class ChromadbArguments(BaseModel):
    requestBody: Dict[str, Any]

class GoogleSearchResultItem(BaseModel):
    result_number: int
    title: str
    description: str
    long_description: Optional[str]
    url: str

class GoogleSearchResults(BaseModel):
    results: List[GoogleSearchResultItem]

class ChromadbResult(BaseModel):
    title: str
    url: str
    document: str

class EmitData(BaseModel):
    function: str
    result: Optional[Any] = None
    error: Optional[str] = None

def extract_relevant_keys(data: Dict[str, Any], model: BaseModel) -> Dict[str, Any]:
    """
    Recursively extract relevant keys from nested dictionaries based on the fields of a Pydantic model.
    """
    relevant_data = {}
    model_fields = model.__fields__.keys()

    def recursive_extract(d: Dict[str, Any], parent_key: str = ''):
        for key, value in d.items():
            if key in model_fields:
                relevant_data[key] = value
            elif isinstance(value, dict):
                recursive_extract(value, key)
            elif parent_key and parent_key in model_fields:
                relevant_data[parent_key] = d

    recursive_extract(data)
    return relevant_data
