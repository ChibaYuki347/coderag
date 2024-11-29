import json
from promptflow import tool



# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def create_chat_response(generate_code_response:str) -> str:
    json_response = json.loads(generate_code_response)
    chat_output = json_response['chat_output']
    codes = json_response['codes']

    code_output = ''

    for code in codes:
        try:
            code_name = code['name']
            code_content = code['output']
            code_output += f'\n\n## {code_name}\n \n ```\n{code_content}\n```\n'
        except:
            print('name or output not found')
            continue
        

    
    return chat_output + code_output
