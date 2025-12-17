import os
from dotenv import load_dotenv


# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

# Loads variables from .env file into environment
load_dotenv()


# --------------------------------------------------
# API Server Configuration
# --------------------------------------------------

# Host and port for FastAPI server
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))


# --------------------------------------------------
# Gemini (LLM) Configuration
# --------------------------------------------------

# API key for Google Gemini (optional)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# --------------------------------------------------
# Embedding & Recommendation Settings
# --------------------------------------------------

# Sentence Transformer model used for embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Maximum number of recommendations returned to client
MAX_RECOMMENDATIONS = 10

# Minimum similarity score threshold (not enforced yet)
SIMILARITY_THRESHOLD = 0.3


# --------------------------------------------------
# Data & Model File Paths
# --------------------------------------------------

# Processed assessment catalog
DATA_PATH = "shl_assessments.csv"

# Saved sentence embeddings
EMBEDDINGS_PATH = "assessments_embeddings.npy"

# FAISS vector index
FAISS_INDEX_PATH = "faiss_index.bin"

# Metadata mapping for assessments
METADATA_PATH = "assessments_metadata.json"
