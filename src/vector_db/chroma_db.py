from typing import Sequence, Dict, Union
from pathlib import Path
import numpy as np
import json
from chromadb import Client
from chromadb.config import Settings
from config import VECTOR_DB_DIR


class ChromaDB:
    EmbeddingsType = Union[np.ndarray, Sequence[Sequence[float]]]
    MetadataType = Dict[str, Union[str, int, float, bool, None]]
    DocumentType = str

    def __init__(self, persist_dir: Path, collection_name: str):
        persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = Client(
            Settings(is_persistent=True, persist_directory=str(persist_dir)))
        self._collection = self._client.get_or_create_collection(
            collection_name)

    def add_embeddings(
        self,
        ids: Sequence[str],
        embeddings: EmbeddingsType,
        metadatas: Sequence[MetadataType],
        documents: Sequence[DocumentType],
    ) -> None:
        array_embeddings = np.asarray(embeddings, dtype=np.float32)
        assert array_embeddings.ndim == 2, "Embeddings must be 2D"
        assert len(ids) == len(array_embeddings) == len(metadatas) == len(
            documents), "Input lengths must match"

        # Validate that each metadata dict is JSON-serializable and flat
        for i, metadata in enumerate(metadatas):
            try:
                json.dumps(metadata)
            except TypeError as e:
                raise ValueError(
                    f"Metadata at index {i} is not JSON-serializable: {metadata}"
                ) from e

        existing = set(self._collection.get()["ids"])

        new_data = [(id_, emb, meta, doc) for id_, emb, meta, doc in zip(
            ids, embeddings, metadatas, documents) if id_ not in existing]

        if not new_data:
            return

        filtered_ids, filtered_embs, filtered_meta, filtered_docs = zip(
            *new_data)
        self._collection.add(
            ids=list(filtered_ids),
            embeddings=np.array(filtered_embs, dtype=np.float32),
            metadatas=list(filtered_meta),
            documents=list(filtered_docs),
        )

    def query(
        self,
        query_embedding: Sequence[float],
        top_k: int = 5,
    ) -> Dict:
        return self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=[
                "metadatas",
                "documents",
                "distances",
                "embeddings",
            ],
        )


# TODO: Remove this main function and implement a proper test code.
if __name__ == "__main__":
    from numpy.random import rand

    persist_path = VECTOR_DB_DIR / "test_project"
    db = ChromaDB(persist_path, "test_chunks")

    ids = ["chunk_0", "chunk_1"]
    docs = [
        "int add(int a, int b) { return a + b; }",
        "void hello() { std::cout << \"Hello\" << std::endl; }"
    ]
    metadatas = [{
        "file": "file1.cpp",
        "line": 10
    }, {
        "file": "file2.cpp",
        "line": 42
    }]
    embeddings = rand(2, 768).astype(np.float32)  # mock 768-dim embeddings

    db.add_embeddings(ids, embeddings, metadatas, docs)

    result = db.query(embeddings[0])
    print("Query result:", result)
