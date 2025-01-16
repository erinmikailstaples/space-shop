import os
from pinecone import Pinecone, Index, ServerlessSpec
from langchain_community.embeddings import OpenAIEmbeddings
from config import PINECONE_API_KEY, OPENAI_API_KEY

# Add debug print
print(f"Using PINECONE_API_KEY: {PINECONE_API_KEY is not None}")

# Initialize Pinecone
pc = Pinecone(
    api_key=PINECONE_API_KEY,
    environment="gcp-starter"  # Required for free tier
)

# Create an index with proper spec for free tier
index_name = "jupiter-moons"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ),
        dimension=1536,  # OpenAI embeddings dimension
        metric="cosine"
    )

# Connect to the index
index = pc.Index(index_name)

def create_and_store_embeddings(data):
    embeddings = OpenAIEmbeddings()  # Will use OPENAI_API_KEY from environment
    
    for idx, row in data.iterrows():
        try:
            text = f"{row['Moon Name']}: {row['Document Title']} - {row['Document Content']}"
            embedding = embeddings.embed_query(text)
            
            metadata = {
                "moon_name": row['Moon Name'],
                "title": row['Document Title'],
                "source": row['Source URL']
            }
            
            index.upsert(vectors=[(str(idx), embedding, metadata)])
            print(f"Successfully embedded: {row['Moon Name']}")
        except Exception as e:
            print(f"Error processing {row['Moon Name']}: {e}")

# Example usage
if __name__ == "__main__":
    from data.clean_data import moons_data
    create_and_store_embeddings(moons_data)
