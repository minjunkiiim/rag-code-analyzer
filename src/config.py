from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
RESOURCES_DIR = ROOT_DIR / "resources"
SERVER_DIR = ROOT_DIR / "src" / "server"
STATIC_DIR = SERVER_DIR / "static"
TEMPLATES_DIR = SERVER_DIR / "templates"
CODEBASES_DIR = RESOURCES_DIR / "codebases"
CODEBASE_CONFIGS = {
    "clickhouse": {
        "path": CODEBASES_DIR / "ClickHouse",
        "language": "cpp",
    }
}
CHUNKS_DIR = RESOURCES_DIR / "chunks"
VECTOR_DB_DIR = RESOURCES_DIR / "vector_db"
MODEL_CACHE_DIR = RESOURCES_DIR / "models"
TINYLLAMA_MODEL_PATH = MODEL_CACHE_DIR / "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
