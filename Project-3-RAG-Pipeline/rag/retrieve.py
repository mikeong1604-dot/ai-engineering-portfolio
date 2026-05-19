import pypdf
import anthropic
import os
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
CHROMA_PATH = BASE_DIR / "chromadb"
model = SentenceTransformer('all-MiniLM-L6-v2') # Free model to embed string
load_dotenv()
client = anthropic.Anthropic()
chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
collection = chroma_client.get_collection(name="Financial_Planning")
#collection = chroma_client.get_collection(name="mas_documents")
def retrieve_chunks(question: str, n_results: int = 3) -> list[str]:
    queries = (model.encode(question).tolist()) #You need to use tolist for any numpy array before passing into anything that doesnt use numpy.
    result = collection.query(
        query_embeddings = queries, #Pass in the questions in embedding format.
        n_results = n_results,
    )
    # TODO: Embed the user's question using the same embedding model
    # TODO: Connect to your ChromaDB collection
    # TODO: Query the collection for the n_results most similar chunks
    # TODO: Return the chunk texts
    text = "\n".join(result["documents"][0])
    return text

