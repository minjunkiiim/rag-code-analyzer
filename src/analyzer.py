import json
from pathlib import Path

from config import CODEBASE_CONFIGS, CHUNKS_DIR, VECTOR_DB_DIR
from codebase_analyzer.parser.tree_sitter_parser import TreeSitterCppParser
from codebase_analyzer.embedder.codet5p_embedder import CodeT5pEmbedder
from vector_db.chroma_db import ChromaDB


def run_analysis(codebase_name: str):
    config = CODEBASE_CONFIGS[codebase_name]
    language = config["language"]

    # 1. Parse code and extract functions → save as JSONL
    parser = TreeSitterCppParser(language, codebase_name)
    parser.run()

    # 2. Initialize vector DB
    db = ChromaDB(
        persist_dir=VECTOR_DB_DIR / codebase_name,
        collection_name=f"{codebase_name}_chunks",
    )

    # 3. Stream function chunks from JSONL file
    chunk_path = CHUNKS_DIR / codebase_name / f"{language}_functions.jsonl"
    embedder = CodeT5pEmbedder()
    batch_size = 1

    batch_chunks = []
    with chunk_path.open("r") as f:
        for idx, line in enumerate(f):
            chunk = json.loads(line)
            batch_chunks.append((idx, chunk))

            if len(batch_chunks) == batch_size:
                _process_batch(batch_chunks, codebase_name, embedder, db)
                if idx % 10 == 0:
                    print(f"Processed {idx + 1} chunks...")
                batch_chunks.clear()

    if batch_chunks:
        _process_batch(batch_chunks, codebase_name, embedder, db)
        print(f"Processed final {len(batch_chunks)} chunks.")

    print(f"Finished storing chunks to vector DB for {codebase_name}.")


def _process_batch(batch_chunks, codebase_name, embedder, db):
    codes = [chunk[1]["code"] for chunk in batch_chunks]
    ids = [f"{codebase_name}_{chunk[0]}" for chunk in batch_chunks]
    metadatas = [{
        "file": chunk[1]["file"],
        "start": chunk[1]["start"],
        "end": chunk[1]["end"]
    } for chunk in batch_chunks]
    embeddings = embedder.embed_chunks(codes)
    db.add_embeddings(ids, embeddings, metadatas, codes)


if __name__ == "__main__":
    run_analysis("clickhouse")
