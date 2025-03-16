from pinecone import Pinecone, ServerlessSpec
import pandas as pd
import os
from dotenv import load_dotenv
# from sentence_transformers import SentenceTransformer
from transformers import AutoModel, AutoTokenizer
import torch

# Load environment variables
load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Load text embedding modelpip
# embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# def get_text_embedding(text):
#     """Generate text embeddings using SentenceTransformer."""
#     return embed_model.encode(text).tolist()



# Load model and tokenizer
model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_text_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().tolist()


def create_index(index_name: str, dimension: int = 384):
    """Creates a Pinecone index if it doesn't exist."""
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    if index_name not in pc.list_indexes():
        pc.create_index(
            index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")  # Change region if needed
        )
    
    return pc.Index(index_name)
def upload_chunk(index, text: str, chunk_id: str):
    """Embed and upload text to Pinecone."""
    embedding = get_text_embedding(text)
    index.upsert(vectors=[(chunk_id, embedding, {"text": text})])

def upload_dataset(index_name: str, fname: str):
    """Read the Pokémon CSV file and upload entries to Pinecone."""
    index = create_index(index_name)
    df = pd.read_csv(fname)

    for i, row in df.iterrows():
        text = f"Name: {row['Name']}, Types: {row['Types']}, Abilities: {row['Abilities']}, " \
               f"Height: {row['Height']}, Weight: {row['Weight']}, " \
               f"Base Experience: {row['Base Experience']}, Description: {row['Flavor Text']}"
        upload_chunk(index, text, chunk_id=f"chunk-{i}")

    print(f"Uploaded {len(df)} Pokémon entries to Pinecone.")

# Run upload process
if __name__ == "__main__":
    upload_dataset("pokemon-index", "pokemon_data.csv")
