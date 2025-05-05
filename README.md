# RAG Code Analyzer

This project builds a local Retrieval-Augmented Generation (RAG) system over large-scale C++ open source codebases (e.g., ClickHouse).
It supports code chunking, embedding, and querying using a local vector database and small language models.

## Features
- Symbolic link-based codebase mounting (no git clone logic)
- Function/class-level code chunking (C++)
- Text embedding and vector DB storage (Chroma)
- Query processing and LLM response generation (FastAPI)

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
# Step 1: Ensure symbolic link exists
ln -s /path/to/ClickHouse ./codebases/clickhouse

# Step 2: Process and embed the code
python src/loader.py
python src/embedder.py

# Step 3: Launch API server
uvicorn api.main:app --reload
```

