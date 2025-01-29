import os
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from tqdm import tqdm

def build_rag_database(transcripts_dir="data/transcripts", db_name="rag_db", db_path="data/databases", 
                       huggingface_model="BAAI/bge-base-en-v1.5", chunk_size=1000, chunk_overlap=200, verbose=False):
    """
    Build a Chroma RAG database from transcript text files using Hugging Face embeddings.

    Args:
        transcripts_dir (str, optional): Directory containing transcript `.txt` files. Default is "data/transcripts".
        db_name (str, optional): Name of the database to create. Default is "rag_db".
        db_path (str, optional): Path to save the Chroma database. Default is "data/databases".
        huggingface_model (str, optional): Model name for Hugging Face embeddings. Default is 'BAAI/bge-base-en-v1.5'.
        chunk_size (list, optional): List of chunk sizes for splitting documents. Default is [700].
        chunk_overlap (list, optional): List of chunk overlaps for splitting documents. Default is [200].
        verbose (bool, optional): If True, print progress messages. Default is False.
    """
    # Ensure database directory exists
    db_full_path = os.path.join(db_path, db_name)
    os.makedirs(db_full_path, exist_ok=True)
    
    # Check if database already exists
    if os.path.exists(os.path.join(db_full_path, "index")):
        print(f"Chroma RAG database already exists at {db_full_path}")
        return

    # Load transcript documents from `.txt` files
    loader = DirectoryLoader(transcripts_dir, glob="**/*.txt", loader_cls=TextLoader, show_progress=True)
    docs_data = loader.load()
    if verbose:
        print(f"\nLoaded {len(docs_data)} documents from {transcripts_dir}")

    # Initialize Hugging Face embeddings
    embeddings_model = HuggingFaceEmbeddings(model_name=huggingface_model)
    if verbose:
        print(f"Using Hugging Face embeddings model: {huggingface_model}")

    # Split documents into chunks
    if verbose:
        print(f"Splitting documents with chunk size {chunk_size} and overlap {chunk_overlap}")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[" ", ",", "\n", ". "]
    )
    data_splits = text_splitter.split_documents(docs_data)
    if verbose:
        print(f"Split {len(docs_data)} documents into {len(data_splits)} chunks")

    print(f"{db_full_path=}")
    print(f"{embeddings_model=}")
    print(f"{data_splits[:3]=}")
    # Create and save Chroma database
    vectordb = Chroma.from_documents(
        documents=data_splits,
        embedding=embeddings_model,
        persist_directory= os.path.join(os.getcwd(), "data", "RAG_Database", "rag_db"),
        collection_name="default"
    )
    vectordb.persist()
    print(f"{vectordb._collection.count()=}")
    print(f"{len(vectordb.get()['ids'])=}")
    print(f"{vectordb.get()['ids'][:3]=}")
    if verbose:
        print(f"Chroma RAG database saved at {db_full_path}")
    # del text_splitter, data_splits  # Clean up to save memory
    return vectordb

