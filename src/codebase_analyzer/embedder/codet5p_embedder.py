from typing import List, Dict

from transformers import AutoTokenizer, AutoModel
import torch

from config import MODEL_CACHE_DIR

MODEL_NAME = "Salesforce/codet5p-110m-embedding"


class CodeT5pEmbedder:

    def __init__(self, model_name: str = MODEL_NAME):
        self._tokenizer = AutoTokenizer.from_pretrained(
            model_name, cache_dir=MODEL_CACHE_DIR, trust_remote_code=True)
        self._model = AutoModel.from_pretrained(model_name,
                                                cache_dir=MODEL_CACHE_DIR,
                                                trust_remote_code=True)

    def embed(self, text: str) -> List[float]:
        inputs = self._tokenizer([text],
                                 return_tensors="pt",
                                 padding=True,
                                 truncation=True)
        with torch.no_grad():
            embeddings = self._model(**inputs)
        return embeddings.cpu().numpy().tolist()[0]

    def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        inputs = self._tokenizer(chunks,
                                 return_tensors="pt",
                                 padding=True,
                                 truncation=True)
        with torch.no_grad():
            embeddings = self._model(**inputs)
        return embeddings.cpu().numpy().tolist()


# TODO: Remove this main function and implement a proper test code.
def main():
    embedder = CodeT5pEmbedder()
    result = embedder.embed_chunks(
        ["def foo():\n    return 42", "def bar(x):\n    return x * 2"])

    print(
        f"Generated {len(result)} embedding(s), dimension = {len(result[0])}")


if __name__ == "__main__":
    main()
