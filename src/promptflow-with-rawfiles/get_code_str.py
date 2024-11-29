
from promptflow.core import tool


# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def get_code_str(context: object) -> str:
    '''
    code_files_format example:
    {
      "id": 8,
      "file_name": "**.css",
      "file_extention": "css",
      "file_type": "unknown",
      "file_path": "**.css",
      "code": "************",
      "description": "************"
    },
    '''
    code_context = context['code_files']

    code_context_str = ''

    for doc in code_context:
        code_context_str += f"## {doc['file_name']}\n"
        code_context_str += f"### Description\n"
        code_context_str += f"{doc['description']}\n"
        code_context_str += f"### Code\n"
        code_context_str += f"```{doc['file_extention']}\n"
        code_context_str += f"{doc['code']}\n"
        


    return code_context_str
