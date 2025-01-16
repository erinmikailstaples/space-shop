import os
import pandas as pd
from dotenv import load_dotenv
import pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.document_loaders import DataFrameLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

def init_pinecone():
    """Initialize Pinecone vector store"""
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"),
        environment="gcp-starter"  # Replace with your environment
    )
    
    # Create index if it doesn't exist
    index_name = "jupiter-moons"
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(
            name=index_name,
            metric="cosine",
            dimension=1536  # OpenAI embeddings dimension
        )
    
    return pinecone.Index(index_name)

def load_and_process_data():
    """Load TSV data and process it for vector store"""
    # Read TSV file
    df = pd.read_csv("jupiteratlas/data/jupiter_moons.tsv", sep="\t")
    
    # Combine relevant columns into a single text field
    df['combined_text'] = df.apply(
        lambda x: f"Moon: {x['Moon Name']}\nTitle: {x['Document Title']}\nContent: {x['Document Content']}\nSource: {x['Source URL']}", 
        axis=1
    )
    
    # Create documents using DataFrameLoader
    loader = DataFrameLoader(df, page_content_column="combined_text")
    documents = loader.load()
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    texts = text_splitter.split_documents(documents)
    
    return texts

def initialize_vector_store():
    """Initialize and populate the vector store"""
    # Initialize Pinecone
    index = init_pinecone()
    
    # Load and process data
    texts = load_and_process_data()
    
    # Create vector store
    vector_store = Pinecone.from_documents(
        documents=texts,
        embedding=embeddings,
        index_name="jupiter-moons"
    )
    
    return vector_store

if __name__ == "__main__":
    # Initialize vector store
    vector_store = initialize_vector_store()
    print("Vector store initialized successfully!") 