from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from typing import List
from langchain_core.documents import Document
import os 

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)

# Initialize embedding model and vector store lazily
_embedding_model = None
_vector_store = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        if api_key.startswith("sk-your-") or "your" in api_key:
            raise ValueError("Please replace the placeholder OPENAI_API_KEY with a valid OpenAI API key")
        
        # Use the same proxy API as configured in model_config.json
        _embedding_model = OpenAIEmbeddings(
            api_key=api_key,
            base_url="https://aihub.gz4399.com/v1"
        )
    return _embedding_model

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        embedding_model = get_embedding_model()
        _vector_store = Chroma(
            collection_name="documents", 
            embedding_function=embedding_model, 
            persist_directory="backend/data/chroma_db"
        )
    return _vector_store

# For backward compatibility with imports
vector_store = None  # Will be set to actual vector store when accessed

def load_and_split_document(file_path: str) -> List[Document]:
    """Load and split a document into chunks based on its file type."""
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    
    if file_extension == ".pdf":
        loader = PyPDFLoader(file_path)
    elif file_extension == ".docx":
        loader = Docx2txtLoader(file_path)
    elif file_extension == ".html":
        loader = UnstructuredHTMLLoader(file_path)
    elif file_extension == ".txt":
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        documents = [Document(page_content=text, metadata={"source": file_path})]
        return text_splitter.split_documents(documents)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    documents = loader.load()
    return text_splitter.split_documents(documents)

def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    try:
        splits = load_and_split_document(file_path)
        
        # Add metadata to each split
        for split in splits:
            split.metadata['file_id'] = file_id
        
        vector_store = get_vector_store()
        vector_store.add_documents(splits)
        # vectorstore.persist()
        return True
    except Exception as e:
        print(f"Error indexing document: {e}")
        return False

def delete_doc_from_chroma(file_id: int):
    try:
        vector_store = get_vector_store()
        docs = vector_store.get(where={"file_id": file_id})
        print(f"Found {len(docs['ids'])} document chunks for file_id {file_id}")
        
        vector_store._collection.delete(where={"file_id": file_id})
        print(f"Deleted all documents with file_id {file_id}")
        
        return True
    except Exception as e:
        print(f"Error deleting document with file_id {file_id} from Chroma: {str(e)}")
        return False