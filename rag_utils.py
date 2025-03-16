import os
from pinecone import Pinecone
from transformers import AutoModel, AutoTokenizer
import torch
from dotenv import load_dotenv
import together
import re

# Load environment variables
load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Load text embedding model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_text_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().tolist()

def search_pokemon(index_name: str, query: str, top_k: int = 5):
    try:
        index = pc.Index('pokemon-index')
        query_embedding = get_text_embedding(query)

        # Search Pinecone
        results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

        if not results["matches"]:
            return "No relevant Pokémon found."

        # Extract top 3 results
        top_matches = results["matches"][:3]

        # Format retrieved Pokémon descriptions
        info_blocks = []
        for match in top_matches:
            pokemon_info = match["metadata"]["text"]
            score = match["score"]
            info_blocks.append(f"- {pokemon_info} (Relevance: {score:.2f})")

        info_text = "\n".join(info_blocks)

        # Construct LLM prompt
        llm_prompt = f"""
        You are a Pokémon expert professor. Answer the following question accordingly, using the provided information:

        **User Question:** {query}

        **Relevant Pokémon Information:**
        {info_text}
        Provide the most relevant response using the information provided. Stay kind and helpful, but concise. Avoid discussing information you don't know.
        """

        # Query Together AI
        response = together.Complete.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            prompt=llm_prompt,
            max_tokens=250,
            temperature=0.7
        )

        # Extract text response correctly
        if "choices" in response and response["choices"]:
            raw_text = response["choices"][0]["text"].strip()

            # Remove unwanted formatting (like LaTeX boxed answers)
            cleaned_text = re.sub(r"\$\s*\\boxed\{.*?\}", "", raw_text).strip()

            return cleaned_text
        else:
            return f"Error: Unexpected response format - {response}"

    except Exception as e:
        return f"Error during search or LLM query: {str(e)}"
