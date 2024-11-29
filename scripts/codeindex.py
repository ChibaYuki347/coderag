from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, ContentFormat
from azure.core.credentials import AzureKeyCredential
import json
import os
import sqlite3
from typing import List,Dict,Any
from openai import AzureOpenAI
import re

from load_azd_env import load_azd_env
from create_database import create_connection, create_database

def get_files(directory:str) -> List[Dict[str, str]]:
    files_list = []
    for root, _, files in os.walk(directory):
        print(f"Walking through: {root}")  # debug root directory
        for file in files:
            # judge file type
            if "code-standard" in root:
                file_type = "code-standard"
            elif "design" in root:
                file_type = "design"
            else:
                file_type = "unknown"
            
            
            print(f"Founded file in get_files: {file}")
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, directory)
            file_name, file_extension = os.path.splitext(file)  # split file name and extension
            file_extension = file_extension.lstrip('.')  # delete the dot from the extension
            files_list.append({'file_name': f'{file_name}.{file_extension}', 'file_extention': file_extension,'file_type': file_type, 'file_path': relative_path})
    return files_list

def insert_code_into_db(conn, file_name, file_extention, file_path, code, description):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO code_files (file_name, file_extention, file_path, code, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (file_name, file_extention, file_path, code, description))
    conn.commit()

def insert_doc_into_db(conn, file_name, file_extention, file_type, file_path, text):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO doc_files (file_name, file_extention, file_type, file_path, text)
        VALUES (?, ?, ?, ?, ?)
    ''', (file_name, file_extention, file_type, file_path, text))
    conn.commit()

def insert_chunked_code_into_db(conn, parent_id, name, code, description):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chunked_codes (parent_id, name, code, description)
        VALUES (?, ?, ?, ?)
    ''', (parent_id, name, code, description))
    conn.commit()

def insert_chunked_doc_into_db(conn, parent_id, section, text):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chunked_docs (parent_id, section, text)
        VALUES (?, ?, ?)
    ''', (parent_id, section, text))
    conn.commit()

def get_code_description_template_list(code:str) -> List[Dict[str, Any]]:
    DEFAULT_TEMPLATE= """
    あなたは、コードを説明する文章を作成するプロの開発者です。
    与えられたコードを読んで、そのコードが何をしているのかを説明してください。
    特に入力と出力に着目してください。
    
    下記のセクションで作成してください。
    
    - 他ファイルのインポートがあれば情報を残します
    - 関数のリストを作成します。それぞれの入力と出力について説明します
    - その他、コードの構造や目的、ユースケースについて説明します
    """

    prompt_list = [
        {"role": "system", "content": DEFAULT_TEMPLATE},
        {"role": "user", "content": f"コードを説明してください。\n{code}"}
    ]

    print("prompt_list: ", prompt_list)  # デバッグ用

    return prompt_list


def get_description_from_openai(code:str, azure_openai_endpoint:str, azure_openai_key:str) -> str:
    client = AzureOpenAI(
        api_key=azure_openai_key,
        api_version='2023-05-15',
        azure_endpoint=azure_openai_endpoint
    )

    template_list = get_code_description_template_list(code)

    generated_response = client.chat.completions.create(
        model='gpt4o',
        messages=template_list,
    )

    description = generated_response.choices[0].message.content
    return description

def get_markdown_from_pdf(pdf_path:str,intelligence_endpoint:str, intelligence_key:str) -> List[str]:
    document_intelligence_client = DocumentIntelligenceClient(endpoint=intelligence_endpoint, credential=AzureKeyCredential(intelligence_key))
    with open(pdf_path, "rb") as f:
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-layout", analyze_request=f, content_type="application/octet-stream",
            output_content_format=ContentFormat.MARKDOWN
        )
    result: AnalyzeResult = poller.result()

    return [result.content,result.pages]


def get_chunked_code_template(code:str) -> List[Dict[str, Any]]:
    DEFAULT_TEMPLATE = """
    あなたは、コードをチャンクに分割するプロの開発者です。
    与えられたコードを読んで、そのコードをチャンクに分割してください。
    チャンクとは、コードの意味を持つ最小単位です。

    具体的にはクラス、関数ベースで意味的に分けた上で、名前を抜き出し、コードの説明を追加してください。
    出力形式は以下です。
    ```json
    {"chunked_codes": [{"name": "チャンク名", "code": "チャンクのコード", "description": "チャンクの説明"}]}
    ```
    - nameは、クラスや関数の名前を使用します
    - codeは、そのクラスや関数のコードを使用します
    - descriptionは、そのクラスや関数の説明を使用します
    """

    prompt_list = [
        {"role": "system", "content": DEFAULT_TEMPLATE},
        {"role": "user", "content": f"コードをチャンクに分割してください。\n{code}"}
    ]

    print("prompt_list: ", prompt_list)  # デバッグ用

    return prompt_list

def get_chunked_code(code:str,azure_openai_endpoint:str, azure_openai_key:str) -> List[Dict[str, Any]]:
    chunked_code = []
    client = AzureOpenAI(
        api_key=azure_openai_key,
        api_version='2023-05-15',
        azure_endpoint=azure_openai_endpoint
    )

    template_list = get_chunked_code_template(code)

    generated_response = client.chat.completions.create(
        model='gpt4o',
        messages=template_list,
        response_format={"type": "json_object"}
    )

    response_content = generated_response.choices[0].message.content
    try:
        response_dict = json.loads(response_content)
    except json.JSONDecodeError:
        return []
    chunked_code = response_dict['chunked_codes']
    return chunked_code

def chunk_markdown(markdown_text):
    chunks = re.split(r'(#+ .*)', markdown_text)  # 見出しで分割
    result = []
    for i in range(1, len(chunks), 2):  # 見出しと内容をペアに
        result.append({'header': chunks[i], 'content': chunks[i + 1].strip()})
    return result

def pages_list(pages:dict):
    pages_list = []
    for page in pages:
        words = page['words']
        words = [word['content'] for word in words]
        words_str = ''.join(words)
        page_dict = {
            'page_number': page['pageNumber'],
            'words': words_str,
        }
        pages_list.append(page_dict)
    return pages_list

def main():
    #  load azd env
    load_azd_env()

    # Set up environment variables
    azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    azure_openai_key = os.getenv('AZURE_OPENAI_KEY')
    azure_documentintelligence_endpoint = os.getenv('AZURE_AI_SERVICES_ENDPOINT')
    azure_documentintelligence_key = os.getenv('AZURE_AI_SERVICES_KEY')
    skip_code_index = os.getenv('SKIP_CODE_INDEX', False)
    skip_doc_index = os.getenv('SKIP_DOC_INDEX', False)

    if skip_code_index == True and skip_doc_index == True:
        print("Skip code and doc indexing")
        return
    
    if skip_code_index == False:
        print("Start code indexing")
        # store code files in the data/codes directory
        code_directory = 'data/codes'
        db_name = 'code_files.db'

        code_files = get_files(code_directory)
        print(f"Code files: {code_files}")

        create_database(db_name)
        conn = create_connection(db_name)

        for id,file_info in enumerate(code_files):
            file_name = file_info['file_name']
            file_path = file_info['file_path']
            file_extention = file_info['file_extention']
            if file_extention == 'DS_Store':
                print(f"Skip file: {file_path}")
                continue
            print(f"Processing file: {file_path}")
            search_path = os.path.join(code_directory, file_path)
            with open(search_path, 'r') as file:
                code = file.read()
                print(f"Code: \n{code}")
                description = get_description_from_openai(code,azure_openai_endpoint=azure_openai_endpoint,azure_openai_key=azure_openai_key)
                insert_code_into_db(conn, file_name, file_extention, file_path, code, description)
                chunked_code = get_chunked_code(code,azure_openai_endpoint=azure_openai_endpoint,azure_openai_key=azure_openai_key)
                if not chunked_code:
                    continue
                
                for chunk in chunked_code:
                    try:
                        name = chunk['name']
                        code = chunk['code']
                        description = chunk['description']
                    except KeyError:
                        print(f"file_path: {file_path} is KeyError")
                        continue
                    insert_chunked_code_into_db(conn, id + 1, name, code, description)
            conn.close()
        


    # store_documents
    if skip_doc_index == True:
        print("Skip doc indexing")
        return
    
    conn = create_connection('code_files.db')
    db_name = 'code_files.db'

    docs_directory = 'data/docs'
    create_database(db_name)
    conn = create_connection(db_name)

    doc_files = get_files(docs_directory)
    print(f"Doc files: {doc_files}") 

    for index, file_info in enumerate(doc_files):
        file_name = file_info['file_name']
        file_path = file_info['file_path']
        file_extention = file_info['file_extention']
        file_type = file_info['file_type']
        print(f"Processing file: {file_path}")
        print(f"File extention: {file_extention}")
        search_path = os.path.join(docs_directory, file_path)
        if file_extention == 'pdf':
            text, pages = get_markdown_from_pdf(search_path, intelligence_endpoint=azure_documentintelligence_endpoint, intelligence_key=azure_documentintelligence_key)
            pages_list_result = pages_list(pages)
            for page in pages_list_result:
                page_number = page['page_number']
                words = page['words']
                insert_chunked_doc_into_db(conn, index + 1, f'Page{page_number}', words)
        elif file_extention == 'md':
            with open(search_path, 'r') as file:
                text = file.read()
                chunked_text = chunk_markdown(text)
                for chunk in chunked_text:
                    section = chunk['header']
                    text = chunk['content']
                    insert_chunked_doc_into_db(conn, index + 1, section, text)
            print(f"Text: \n{text}")
        else:
            continue
        insert_doc_into_db(conn, file_name, file_extention, file_type, file_path, text)

    conn.close()

if __name__ == '__main__':
    main()