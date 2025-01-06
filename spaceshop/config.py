import os
from dotenv import load_dotenv
from pathlib import Path

base_dir = Path(__file__).resolve().parent

env_path = base_dir / '.env'
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
