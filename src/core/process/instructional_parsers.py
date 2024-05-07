
from openai import OpenAI
import os 
import json 

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def openai_create_golfer_profile(parsing_string):

    prompt=f"""you excel at parsing the string into a json,here is a string: {parsing_string}, can you provide the json for this
    use title and url as the fields.
    """

    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=1350,
        n=1,
        stop=None,
        temperature=0.9,
    )
    # print(response)
    answer_json_string=(response.model_dump_json(indent=2))
    answer_dict = json.loads(answer_json_string)
    # answer = answer_dict['choices'][0]['message']['content']
    answer = answer_dict['choices'][0]['text']
    dict_input = json.loads(answer)

    # answer = response.choices[0].message['content'].strip()
    # print(answer)
    # print(answer_dict)
    # print(type(answer_dict))
    # print(type(answer))
    # print(type(dict_input))
    return dict_input

# string="'Speech by The Right Hon. The Lord Burnett of Maldon: The Age of Algorithms and Artificial Intelligence', 'https://www.bailii.org/bailii/lecture/2018/BAILII_Lecture_2018.pdf'"

# openai_create_golfer_profile(string)