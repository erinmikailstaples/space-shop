import os
from pinecone import Pinecone, Index, ServerlessSpec
from langchain_community.embeddings import OpenAIEmbeddings
from config import PINECONE_API_KEY, OPENAI_API_KEY

# Add debug print
print(f"Using PINECONE_API_KEY: {PINECONE_API_KEY is not None}")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

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
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
    
    for idx, row in data.iterrows():
        # Using the correct column names from your TSV file
        text = f"{row['Moon Name']}: {row['Document Title']} - {row['Document Content']}"
        embedding = embeddings.embed_query(text)
        
        metadata = {
            "moon_name": row['Moon Name'],
            "title": row['Document Title'],
            "source": row['Source URL']
        }
        
        # Store with metadata
        index.upsert(vectors=[(str(idx), embedding, metadata)])

# Example usage
if __name__ == "__main__":
    from data.clean_data import moons_data
    create_and_store_embeddings(moons_data)
