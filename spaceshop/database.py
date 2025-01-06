import os
from pinecone import Pinecone
from langchain_community.embeddings import OpenAIEmbeddings
from config import PINECONE_API_KEY, OPENAI_API_KEY

# Initialize Pinecone with the new approach
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create an index
index_name = "jupiter-moons"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # OpenAI embeddings are 1536 dimensions
        metric='cosine'
    )

# Connect to the index
index = pc.Index(index_name)

def create_and_store_embeddings(data):
    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

    # Iterate over your data and create embeddings
    for idx, row in data.iterrows():
        # Using 'Document Content' column from your TSV file
        text = row['Document Content']
        embedding = embeddings.embed_query(text)
        
        # Store the embedding in Pinecone
        index.upsert(vectors=[(str(idx), embedding, {"text": text})])

# Example usage
if __name__ == "__main__":
    from data.clean_data import moons_data
    create_and_store_embeddings(moons_data)
