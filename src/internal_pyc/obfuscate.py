"""
obfuscate.py  – Perceptronix Ltd internal tooling
Compiles a .py source file to an optimised .pyc bytecode file,
then optionally removes the source.  Intended for pre-deployment
preparation only; never committed to client repos.

Usage:
    python obfuscate.py <source.py> [--remove-source]
"""
import sys
import os
import py_compile
import shutil
import argparse


def compile_to_pyc(src_path: str, remove_source: bool = False) -> str:
    """Compile *src_path* to an optimised .pyc and return the output path."""
    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"Source not found: {src_path}")

    # py_compile writes into __pycache__; we want the .pyc sitting next to the
    # source (or in the deploy bundle) so we copy it out afterwards.
    py_compile.compile(src_path, optimize=2, doraise=True)

    # Locate the generated .pyc (inside __pycache__)
    import importlib.util, importlib
    cache_path = importlib.util.cache_from_source(src_path, optimization=2)

    # Place .pyc alongside the source file with a plain name
    base = os.path.splitext(src_path)[0]
    dest_pyc = base + ".pyc"
    shutil.copy2(cache_path, dest_pyc)

    if remove_source:
        os.remove(src_path)
        print(f"[obfuscate] source removed: {src_path}")

    print(f"[obfuscate] compiled → {dest_pyc}")
    return dest_pyc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile .py → .pyc and optionally remove source.")
    parser.add_argument("source", help=".py file to compile")
    parser.add_argument("--remove-source", action="store_true",
                        help="Delete the .py after successful compilation")
    args = parser.parse_args()
    compile_to_pyc(args.source, remove_source=args.remove_source)
