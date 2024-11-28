import os
import sqlite3
from typing import List,Dict,Any
from openai import AzureOpenAI

from load_azd_env import load_azd_env
from create_database import create_connection, create_database
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, ContentFormat

def get_files(directory:str) -> List[Dict[str, str]]:
    files_list = []
    for root, _, files in os.walk(directory):
        print(f"Walking through: {root}")  # debug root directory
        for file in files:
            # if file.endswith('.py') or file.endswith('.js'):
            print(f"Founded file in get_files: {file}")
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, directory)
            file_name, file_extension = os.path.splitext(file)  # split file name and extension
            file_type = file_extension.lstrip('.')  # delete the dot from the extension
            files_list.append({'file_name': file_name,'file_type': file_type, 'file_path': relative_path})
    return files_list

def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS code_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            code TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

def insert_code_into_db(conn, file_name, file_type, file_path, code, description):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO code_files (file_name, file_type, file_path, code, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (file_name, file_type, file_path, code, description))
    conn.commit()

def insert_doc_into_db(conn, file_name, file_type, file_path, text):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO doc_files (file_name, file_type, file_path, text)
        VALUES (?, ?, ?, ?)
    ''', (file_name, file_type, file_path, text))
    conn.commit()

def get_template_list(code:str) -> List[Dict[str, Any]]:
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

    template_list = get_template_list(code)

    generated_response = client.chat.completions.create(
        model='gpt4o',
        messages=template_list,
    )

    description = generated_response.choices[0].message.content
    return description

def get_markdown_from_pdf(pdf_path:str,intelligence_endpoint:str, intelligence_key:str) -> str:
    document_intelligence_client = DocumentIntelligenceClient(endpoint=intelligence_endpoint, credential=AzureKeyCredential(intelligence_key))
    with open(pdf_path, "rb") as f:
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-layout", analyze_request=f, content_type="application/octet-stream",
            output_content_format=ContentFormat.MARKDOWN
        )
    result: AnalyzeResult = poller.result()

    return result.content

def main():
    #  load azd env
    load_azd_env()

    # Set up environment variables
    azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    azure_openai_key = os.getenv('AZURE_OPENAI_KEY')
    azure_documentintelligence_endpoint = os.getenv('AZURE_AI_SERVICES_ENDPOINT')
    azure_documentintelligence_key = os.getenv('AZURE_AI_SERVICES_KEY')

    # store code files in the data/codes directory
    code_directory = 'data/codes'
    db_name = 'code_files.db'

    code_files = get_files(code_directory)
    print(f"Code files: {code_files}")

    create_database(db_name)
    conn = create_connection(db_name)

    for file_info in code_files:
        file_name = file_info['file_name']
        file_path = file_info['file_path']
        file_type = file_info['file_type']
        print(f"Processing file: {file_path}")
        search_path = os.path.join(code_directory, file_path)
        with open(search_path, 'r') as file:
            code = file.read()
            print(f"Code: \n{code}")
            description = get_description_from_openai(code,azure_openai_endpoint=azure_openai_endpoint,azure_openai_key=azure_openai_key)
            insert_code_into_db(conn, file_name, file_type, file_path, code,description)

    # store_document

    docs_directory = 'data/docs'
    conn = create_database(db_name)

    doc_files = get_files(docs_directory)
    print(f"Doc files: {doc_files}") 

    for file_info in doc_files:
        file_name = file_info['file_name']
        file_path = file_info['file_path']
        file_type = file_info['file_type']
        print(f"Processing file: {file_path}")
        print(f"File type: {file_type}")
        search_path = os.path.join(docs_directory, file_path)
        if file_type == 'pdf':
            text = get_markdown_from_pdf(search_path, intelligence_endpoint=azure_documentintelligence_endpoint, intelligence_key=azure_documentintelligence_key)
        else:
            with open(search_path, 'r') as file:
                text = file.read()
            print(f"Text: \n{text}")
        insert_doc_into_db(conn, file_name, file_type, file_path, text)

    conn.close()

if __name__ == '__main__':
    main()