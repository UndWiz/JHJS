# CALEB: Creative Automation & Local Engineering Builder

CALEB is a local, privacy-first AI development agent engineered to autonomously construct, maintain, and manage a modular software studio environment.

## System Requirements
- OS: Linux (Tested on Mint 22.3)
- Python 3.x + `venv`
- Local Inference: [Ollama](https://ollama.com/) running `qwen2.5-coder:7b`

## Quick Start
1. Ensure the Ollama daemon is active: `systemctl start ollama` or `ollama serve`.
2. Verify the model is available: `ollama run qwen2.5-coder:7b`.
3. Launch the studio environment: `./start_caleb.sh`.

## Core Features & Tool Schema
CALEB interacts with the local filesystem via a strict XML tool schema, automatically parsed by the Agent Controller:
- `<write_file path="file.py">content</write_file>`: Scaffolds new files.
- `<patch_file path="file.py" line_start="10" line_end="20">content</patch_file>`: Context-efficient line replacement.
- `<run_command>cmd</run_command>`: Executes terminal commands with an autonomous self-repair loop on non-zero exit codes.
- `<read_file>path</read_file>`: Inspects existing code before patching.

## Architecture Modules
- **Memory Manager (SQLite3):** Retains sliding-window context, file diffs, and execution logs.
- **Code Indexer:** Uses Python AST to auto-generate `PROJECT_MAP.md` tracking dependencies and structures.
- **Hardware Monitor:** Real-time polling of CPU, RAM, and VRAM ensuring execution stays within safety limits.
- **Sandboxing:** Path traversal protection and execution blacklists prevent destructive terminal operations.
