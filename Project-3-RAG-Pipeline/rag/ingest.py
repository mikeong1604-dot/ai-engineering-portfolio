import pypdf #Does not work on scanned documents, only text-based PDFs.
import anthropic
import os
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CHROMA_PATH = BASE_DIR / "chromadb"
load_dotenv()
model = SentenceTransformer('all-MiniLM-L6-v2')
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH)) # Set up persistent ChromaDB client with a local directory for storage
def create_collection(name: str): # Only need to create client and collection once.
    collection = chroma_client.create_collection(name)
 #Set up persistent ChromaDB client with a local directory for storage
    return
#chroma_client = chromadb.PersistentClient(path="C:\\Users\\mikeo\\Projects\\Project1-CLI\\rag\\chromadb") # Set up persistent ChromaDB client with a local directory for storage
#collection = chroma_client.create_collection(name="mas_documents")


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    # TODO: Use model.encode() to embed all chunks
    # TODO: Convert output to a list of lists (not numpy arrays)
    # Return the embeddings
    embeddings = model.encode(chunks).tolist()
    return embeddings
    

def extract_text(pdf_path: str):
    output = []
    pdf = pypdf.PdfReader(pdf_path)
    pages = pdf.pages
    for page in pages:
        text = page.extract_text()
        output.append(text)
    return "\n".join(output)
    # TODO: Open the PDF using pypdf.PdfReader
    # TODO: Loop through all pages
    # TODO: Extract text from each page
    # TODO: Join all pages into one string and return it
def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    output = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end > len(text):
            end = len(text)
            output.append(text[start:end])
            break
        output.append(text[start:end])
        start = end - overlap  # Move back by overlap for the next chunk
    return output
    # TODO: Split text into chunks of chunk_size characters
    # TODO: Each chunk should overlap with the previous by `overlap` characters
    # TODO: Return a list of chunk strings
def store_chunks(chunks: list[str], embeddings: list[list[float]]):
    collection.add(
        ids = [str(i) for i in range(len(chunks))],
        documents = chunks,
        embeddings = embeddings,
    )
    # TODO: Create a ChromaDB client (persistent, not in-memory)
    # TODO: Create or get a collection called "mas_documents"
    # TODO: Add chunks as documents with their embeddings
    # TODO: Each document needs a unique ID — use the chunk index
    print("Chunks stored successfully")
    return


#create_collection("Financial_Planning")
#collection = chroma_client.get_collection(name="Financial_Planning") # Get the collection you created
#print(collection.get())
#chunks = chunk_text(text,5000,500)
#embeddings = embed_chunks(chunks)
#store_chunks(chunks, embeddings)
