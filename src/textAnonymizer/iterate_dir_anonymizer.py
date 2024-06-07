# iterate_dir_anonymizer.py

import os
import text_anonymizer

def anonymize_file(file_path, output_dir):
    with open(file_path, 'r') as file:
        text = file.read()
    anonymized_text = text_anonymizer.anonymize(text, name_types=[
        "PERSON", "NORP", "FAC", "ORG", "GPE", "LOC", "PRODUCT", 
        "EVENT", "WORK_OF_ART", "LANGUAGE", "DATE", 
        "TIME", "PERCENT", "MONEY", "QUANTITY"
    ], fictional=False)
    
    output_file_path = os.path.join(output_dir, os.path.basename(file_path))
    with open(output_file_path, 'w') as output_file:
        output_file.write(anonymized_text)
    print(f"Anonymized file saved to: {output_file_path}")

def iterate_directory(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    txt_files = [file_name for file_name in os.listdir(input_dir) if file_name.endswith('.txt')]
    
    for file_name in txt_files:
        file_path = os.path.join(input_dir, file_name)
        anonymize_file(file_path, output_dir)
        print(f"Processed file: {file_path}")

if __name__ == "__main__":
    input_dir = '/media/taymur/EXTERNAL_USB/large/legal_datasets/contractsdataset/contracts_2020'  # Change to your input directory
    output_dir = '/media/taymur/EXTERNAL_USB/large/legal_datasets/contractsdataset/annonymised_contracts'  # Change to your output directory
    iterate_directory(input_dir, output_dir)
