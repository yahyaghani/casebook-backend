import re

# # Sample para variable provided by the user
# para = """
# Here are the extracted details from the provided text:


# Entities: 
# - [2024] EWCA Crim 312
# - Vice President of the Court of Appeal Criminal Division (Lord Justice Holroyde)
# - Mr Justice Picken
# - Mrs Justice Farbey DBE
# - R v Kathleen Crane
# - Royal Courts of Justice, London
# - Fraud Act 2006
# - Criminal Appeal Act 1968

# Labels: 
# - DATE
# - JUDGE
# - JUDGE
# - JUDGE
# - CASENAME
# - COURT
# - LEGAL_PROVISION
# - LEGAL_PROVISION
# """



def parse_entities_labels_from_openai(para):

    entity_pattern = r"Entities:\s*(.*)Labels:"
    label_pattern = r"Labels:\s*(.*)"

    # Extract entities and labels using regular expressions
    entities_match = re.search(entity_pattern, para, re.DOTALL)
    labels_match = re.search(label_pattern, para, re.DOTALL)

    # Extract entities and labels as lists
    entities = entities_match.group(1).strip().split('\n')
    labels = labels_match.group(1).strip().split('\n')

    # Remove leading hyphen and space ("- ") and rename "LEGAL_PROVISION" to "PROVISION"
    entities = [entity.strip()[2:] if entity.strip().startswith("- ") else entity.strip() for entity in entities]
    labels = [label.strip()[2:] if label.strip().startswith("- ") else label.strip() for label in labels]
    labels = ['PROVISION' if label == 'LEGAL_PROVISION' else label for label in labels]

    # Filter out labels not included in the desired list
    desired_labels = ['CASENAME', 'JUDGE', 'COURT', 'PROVISION', 'CITATION']
    ents = [(entities[i], labels[i]) for i in range(len(entities)) if labels[i] in desired_labels]

    # print(ents)
    # print(type(ents))
    return ents
# parse_entities_labels_from_openai(para)

# print(entities)
# print(labels)


def parse_legal_insights(text):
    # Define a pattern that matches the numbered items
    # This pattern captures numbers followed by periods and considers potential bold markdown
    pattern = re.compile(r'\n(\d+)\.\s*\*\*(.*?)\*\*:([^:]*?)(?=\n\d|\n\n|openai-recommendations|$)', re.S)
    
    # Use findall to extract all matches
    matches = pattern.findall(text)
    
    # Process matches to format them into a list of insights
    insights = [f"{num}. {title.strip()}: {description.strip()}" for num, title, description in matches]
    
    return insights
