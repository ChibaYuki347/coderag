import json
import os
import requests

from load_azd_env import load_azd_env

def create_code_index(code_index_name:str, ai_search_endpoint:str,ai_search_key:str, azure_openai_endpoint:str, azure_openai_key:str, text_embedding_model:str):
    index_payload = {
    "name": code_index_name,
    "defaultScoringProfile": None,
    "fields": [
      { "name": "id", "type": "Edm.String", "searchable": True, "filterable": True, "retrievable": True, "stored": True, "sortable": True, "facetable": True, "key": True, "indexAnalyzer": None, "searchAnalyzer": None, "analyzer": "keyword", "dimensions": None, "vectorSearchProfile": None, "vectorEncoding": None, "synonymMaps": []    },
      { "name": "code_id", "type": "Edm.Int32", "searchable": False, "filterable": False, "retrievable": True, "stored": True, "sortable": False, "facetable": False, "key": False, "indexAnalyzer": None, "searchAnalyzer": None, "analyzer": None, "dimensions": None, "vectorSearchProfile": None, "vectorEncoding": None, "synonymMaps": []    },
      { "name": "file_name", "type": "Edm.String", "searchable": True, "retrievable": "true", "facetable": "true", "filterable": "true", "sortable": "false"},
      { "name": "file_extention", "type": "Edm.String", "searchable": False, "retrievable": "true", "facetable": "true", "filterable": "true", "sortable": "false"},
      { "name": "file_path", "type": "Edm.String", "searchable": False, "retrievable": "true", "facetable": "true", "filterable": "true", "sortable": "false"},
      { "name": "code", "type": "Edm.String", "searchable": True, "retrievable": "true", "facetable": "true", "filterable": "true", "sortable": "false"},
      { "name": "description", "type": "Edm.String", "searchable": True, "filterable": True, "retrievable": True, "stored": True, "sortable": False, "facetable": False, "key": False, "indexAnalyzer": None, "searchAnalyzer": None, "analyzer": "ja.lucene", "dimensions": None, "vectorSearchProfile": None, "vectorEncoding": None, "synonymMaps": []    },
      { "name": "vector", "type": "Collection(Edm.Single)", "searchable": True, "filterable": False, "retrievable": True, "stored": True, "sortable": False, "facetable": False, "key": False, "indexAnalyzer": None, "searchAnalyzer": None, "analyzer": None, "dimensions": 3072, "vectorSearchProfile": "vector-profile", "vectorEncoding": None, "synonymMaps": []    }
    ],
    "scoringProfiles": [],
    "corsOptions": None,
    "suggesters": [],
    "analyzers": [],
    "tokenizers": [],
    "tokenFilters": [],
    "charFilters": [],
    "encryptionKey": None,
    "similarity": {
      "@odata.type": "#Microsoft.Azure.Search.BM25Similarity",
      "k1": None,
      "b": None
    },
    "semantic": None,
    "vectorSearch": {
      "algorithms": [
        {
          "name": "vector-algorithm",
          "kind": "hnsw",
          "hnswParameters": {
            "metric": "cosine",
            "m": 4,
            "efConstruction": 400,
            "efSearch": 500
          },
          "exhaustiveKnnParameters": None
        }
      ],
      "profiles": [
        {
          "name": "vector-profile",
          "algorithm": "vector-algorithm",
          "vectorizer": "vector-vectorizer",
          "compression": None
        }
      ],
      "vectorizers": [
        {
          "name": "vector-vectorizer",
          "kind": "azureOpenAI",
          "azureOpenAIParameters": {
            "resourceUri": azure_openai_endpoint,
            "deploymentId": 'embedding',
            "apiKey": azure_openai_key,
            "modelName": text_embedding_model,
            "authIdentity": None
          },
          "customWebApiParameters": None,
        }
      ],
      "compressions": []
    }
  }
    
    headers = {'Content-Type': 'application/json', 'api-key': ai_search_key}
    params = {'api-version': '2024-07-01'}

    r = requests.put(ai_search_endpoint + "/indexes/" + code_index_name,
                    data=json.dumps(index_payload), headers=headers, params=params)
    print(r.status_code)
    print(r.ok)
    print(r.text)

def create_doc_index(doc_index_name:str, ai_search_endpoint:str,ai_search_key:str, azure_openai_endpoint:str, azure_openai_key:str, text_embedding_model:str):
    index_payload = {
    "name": doc_index_name,
    "defaultScoringProfile": None,
    "fields": [
      { "name": "id", "type": "Edm.String", "searchable": True, "filterable": True, "retrievable": True, "stored": True, "sortable": True, "facetable": True, "key": True, "indexAnalyzer": None, "searchAnalyzer": None, "analyzer": "keyword", "dimensions": None, "vectorSearchProfile": None, "vectorEncoding": None, "synonymMaps": []    },
      { "name": "doc_id", "type": "Edm.Int32", "searchable": False, "filterable": False, "retrievable": True, "stored": True, "sortable": False, "facetable": False, "key": False, "indexAnalyzer": None, "searchAnalyzer": None, "analyzer": None, "dimensions": None, "vectorSearchProfile": None, "vectorEncoding": None, "synonymMaps": []    },
      { "name": "file_name", "type": "Edm.String", "searchable": False, "retrievable": "true", "facetable": "true", "filterable": "true", "sortable": "false"},
      { "name": "file_extention", "type": "Edm.String", "searchable": False, "retrievable": "true", "facetable": "true", "filterable": "true", "sortable": "false"},
      { "name": "file_path", "type": "Edm.String", "searchable": False, "retrievable": "true", "facetable": "true", "filterable": "true", "sortable": "false"},
      { "name": "text", "type": "Edm.String", "searchable": True, "filterable": True, "retrievable": True, "stored": True, "sortable": False, "facetable": False, "key": False, "indexAnalyzer": None, "searchAnalyzer": None, "analyzer": "ja.lucene", "dimensions": None, "vectorSearchProfile": None, "vectorEncoding": None, "synonymMaps": []    },
      { "name": "vector", "type": "Collection(Edm.Single)", "searchable": True, "filterable": False, "retrievable": True, "stored": True, "sortable": False, "facetable": False, "key": False, "indexAnalyzer": None, "searchAnalyzer": None, "analyzer": None, "dimensions": 3072, "vectorSearchProfile": "vector-profile", "vectorEncoding": None, "synonymMaps": []    }
    ],
    "scoringProfiles": [],
    "corsOptions": None,
    "suggesters": [],
    "analyzers": [],
    "tokenizers": [],
    "tokenFilters": [],
    "charFilters": [],
    "encryptionKey": None,
    "similarity": {
      "@odata.type": "#Microsoft.Azure.Search.BM25Similarity",
      "k1": None,
      "b": None
    },
    "semantic": None,
    "vectorSearch": {
      "algorithms": [
        {
          "name": "vector-algorithm",
          "kind": "hnsw",
          "hnswParameters": {
            "metric": "cosine",
            "m": 4,
            "efConstruction": 400,
            "efSearch": 500
          },
          "exhaustiveKnnParameters": None
        }
      ],
      "profiles": [
        {
          "name": "vector-profile",
          "algorithm": "vector-algorithm",
          "vectorizer": "vector-vectorizer",
          "compression": None
        }
      ],
      "vectorizers": [
        {
          "name": "vector-vectorizer",
          "kind": "azureOpenAI",
          "azureOpenAIParameters": {
            "resourceUri": azure_openai_endpoint,
            "deploymentId": 'embedding',
            "apiKey": azure_openai_key,
            "modelName": text_embedding_model,
            "authIdentity": None
          },
          "customWebApiParameters": None,
        }
      ],
      "compressions": []
    }
  }
    
    headers = {'Content-Type': 'application/json', 'api-key': ai_search_key}
    params = {'api-version': '2024-07-01'}

    r = requests.put(ai_search_endpoint + "/indexes/" + doc_index_name,
                    data=json.dumps(index_payload), headers=headers, params=params)
    print(r.status_code)
    print(r.ok)
    print(r.text)


def main():
    # load environment variables
    load_azd_env()

    # Get the environment variables
    AZURE_SEARCH_KEY = os.getenv('AZURE_SEARCH_KEY')
    AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
    CODE_INDEX_NAME = os.getenv('CODE_INDEX_NAME', 'code-index')
    DOC_INDEX_NAME = os.getenv('DOC_INDEX_NAME', 'doc-index')
    AOAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AOAI_KEY = os.getenv('AZURE_OPENAI_KEY')
    TEXT_EMBEDDING_MODEL = os.getenv('AZURE_OPENAI_EMBEDDING_MODEL')

    # Create the code index
    create_code_index(CODE_INDEX_NAME, AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, AOAI_ENDPOINT, AOAI_KEY, TEXT_EMBEDDING_MODEL)

    # Create the doc index
    create_doc_index(DOC_INDEX_NAME, AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, AOAI_ENDPOINT, AOAI_KEY, TEXT_EMBEDDING_MODEL)

    

if __name__ == '__main__':
    main()