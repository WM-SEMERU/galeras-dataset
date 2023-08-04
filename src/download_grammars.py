from git import Git, Repo
from pathlib import Path
from tree_sitter import Language

import ast_tree

_GRAMMARs = {
    "java": ("https://github.com/tree-sitter/tree-sitter-java.git", "tree-sitter-java", "v0.20.0"),
    "python": ("https://github.com/tree-sitter/tree-sitter-python.git", "tree-sitter-python", "v0.20.0"),
}

def download_grammars(
        # languages: Param("Languages to download", str, nargs="+") = "all",
        languages
):
    """Download Tree-sitter grammars"""
    try:
        grammars = _GRAMMARs if languages == "all" else {k: _GRAMMARs[k] for k in languages}
    except KeyError as e:
        raise ValueError(f"Invalid or unsupported language: {e}. Supported languages: {list(_GRAMMARs.keys())}")

    langs = []
    grammar_dir = Path(ast_tree.__file__).parent / "grammars"
    print(grammar_dir)
    grammar_dir.mkdir(exist_ok=True)
    for lang, (url, dir, tag) in grammars.items():
        repo_dir = grammar_dir / dir
        if not repo_dir.exists():
            repo = Repo.clone_from(url, repo_dir)
        g = Git(str(repo_dir))
        g.checkout(tag)
        langs.append(str(repo_dir))

    Language.build_library(
        # Store the library in the directory
        str(grammar_dir / "tree-sitter-languages.so"),
        # Include one or more languages
        langs
    )

download_grammars(["java"])