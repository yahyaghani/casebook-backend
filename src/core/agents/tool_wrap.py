import os
import jsonref
import sys

# Define the relative path from the base directory in PYTHONPATH
relative_path = 'src/core/agents/tool_spec.json'

# Find the base directory in PYTHONPATH
for base_dir in sys.path:
    potential_path = os.path.join(base_dir, relative_path)
    if os.path.exists(potential_path):
        file_path = potential_path
        break
else:
    raise FileNotFoundError(f"{relative_path} not found in PYTHONPATH")

# Load the OpenAPI specification
with open(file_path, 'r') as f:
    openapi_spec = jsonref.loads(f.read())

def openapi_to_functions(openapi_spec):
    functions = []

    for path, methods in openapi_spec["paths"].items():
        for method, spec_with_ref in methods.items():
            spec = jsonref.replace_refs(spec_with_ref)
            function_name = spec.get("operationId")
            desc = spec.get("description") or spec.get("summary", "")

            parameters = {"type": "object", "properties": {}}

            req_body = (
                spec.get("requestBody", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema")
            )
            if req_body:
                parameters["properties"]["requestBody"] = req_body

            params = spec.get("parameters", [])
            if params:
                param_properties = {
                    param["name"]: param["schema"]
                    for param in params
                    if "schema" in param
                }
                parameters["properties"]["parameters"] = {
                    "type": "object",
                    "properties": param_properties,
                }

            functions.append({
                "name": function_name,
                "description": desc,
                "parameters": parameters
            })

    return functions

functions = openapi_to_functions(openapi_spec)
