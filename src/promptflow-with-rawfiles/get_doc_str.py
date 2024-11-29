
from promptflow.core import tool


# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def get_doc_str(context: object) -> str:
    '''
    doc_files_format example:
    {
        "id": 3,
        "file_name": "コーディング規約.md",
        "file_extention": "md",
        "file_type": "code-standard",
        "file_path": "code-standard/コーディング規約.md",
        "text": "- その他細かな修正"
    }
    '''
    doc_context = context['doc_files']

    doc_context_str = ''

    for doc in doc_context:
        doc_context_str += f"## {doc['file_name']}\n"
        doc_context_str += f"### Text\n"
        doc_context_str += f"{doc['text']}\n"
        doc_context_str += f"```\n"


    return doc_context_str
