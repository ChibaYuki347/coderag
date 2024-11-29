
from promptflow.core import tool
import sqlite3
from typing import List, Dict

def fetch_files(db_name: str,table_name:str) -> List[Dict[str, str]]:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name}')
    rows = cursor.fetchall()
    conn.close()

    # カラム名を取得
    column_names = [description[0] for description in cursor.description]

    # 辞書形式で結果を返す
    result = [dict(zip(column_names, row)) for row in rows]
    return result

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def get_context() -> str:
    db_name = '../../code_files.db'
    code_files = fetch_files(db_name, 'code_files')
    doc_files = fetch_files(db_name, 'doc_files')
    for file in code_files:
        print(file)
    
    searched_obj = {
        "code_files": code_files,
        "doc_files": doc_files
    }
    return searched_obj
