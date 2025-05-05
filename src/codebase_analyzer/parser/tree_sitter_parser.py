from typing import TypedDict, List
from pathlib import Path
import json

import tree_sitter_cpp
from tree_sitter import Language, Parser

from config import CODEBASE_CONFIGS, CHUNKS_DIR

PARSER_CONFIGS = {
    "cpp": Language(tree_sitter_cpp.language()),
}


class TreeSitterCppParser:

    class FunctionChunk(TypedDict):
        file: str
        start: int
        end: int
        code: str

    def __init__(self, language: str, codebase: str):
        self._tree_sitter_language = PARSER_CONFIGS[language]
        self._parser = Parser(self._tree_sitter_language)
        self._codebase = codebase
        self._codebase_root = CODEBASE_CONFIGS[codebase]["path"]
        self._output_path = CHUNKS_DIR / self._codebase / f"{language}_functions.jsonl"

    def extract_functions_from_file_(self, path: Path) -> List[FunctionChunk]:
        source = path.read_text()
        parsed_tree = self._parser.parse(source.encode("utf-8"))
        lines = source.splitlines()

        chunks = []
        cursor = parsed_tree.walk()
        visited_nodes = set()
        while cursor.node is not None:
            node = cursor.node
            if node.id in visited_nodes:
                if cursor.goto_next_sibling():
                    continue
                if not cursor.goto_parent():
                    break

            visited_nodes.add(node.id)
            if node.type == "function_definition":
                start = node.start_point[0]
                end = node.end_point[0]
                code = "\n".join(lines[start:end + 1])
                chunks.append({
                    "file":
                    str(path.relative_to(self._codebase_root)),
                    "start":
                    start + 1,
                    "end":
                    end + 1,
                    "code":
                    code,
                })

            if cursor.goto_first_child():
                continue
            if cursor.goto_next_sibling():
                continue
            while not cursor.goto_next_sibling():
                if not cursor.goto_parent():
                    break
            else:
                continue
            break

        return chunks

    def extract_functions_from_root(self) -> List[FunctionChunk]:
        cpp_files = [
            p for p in self._codebase_root.rglob("*")
            if p.suffix in [".cc", ".cpp", ".h", ".hpp"]
        ]

        chunks = []
        for file in cpp_files:
            chunks.extend(self.extract_functions_from_file_(file))

        return chunks

    def run(self):
        cpp_files = [
            p for p in self._codebase_root.rglob("*")
            if p.suffix in [".cc", ".cpp", ".h", ".hpp"]
        ]

        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        count = 0
        with self._output_path.open("w") as f:
            for file in cpp_files:
                chunks = self.extract_functions_from_file_(file)
                for chunk in chunks:
                    f.write(json.dumps(chunk) + "\n")
                count += 1
                if count % 100 == 0:
                    print(f"Processed {count} files...")

        print(
            f"Finished processing {count} files from {self._codebase_root} to {self._output_path}"
        )


# TODO: Remove this main function and implement a proper test code.
def main():
    analyzer = TreeSitterCppParser("cpp", "clickhouse")
    analyzer.run()
    print()


if __name__ == "__main__":
    main()
