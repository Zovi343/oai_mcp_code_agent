# 🐍 MCP Code Agent With OpenAI LLMs
[![Python Version](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3110/) [![MCP Version](https://img.shields.io/badge/MCP-1.5.0-orange?logo=anthropic&logoColor=white)](https://pypi.org/project/mcp/) [![OpenAI Version](https://img.shields.io/badge/OpenAI-1.68.2-lightgrey?logo=openai&logoColor=whit)](https://pypi.org/project/openai/)

## 📘 Overview
This is a Python project designed to interact with the MCP framework and OpenAI LLMs.

## 📦 Installation
First, ensure you have [Poetry installed](https://python-poetry.org/docs/#installation).

```bash
poetry install
```

## 🚀 Running the Project
To run the project, use the following command:
```bash
poetry run python -m src.mcp_code_agent.main
```

## Development Setup
This project uses `pre-commit` to ensure consistent code quality before commits.
```bash
poetry run pre-commit install
```

To manually run hooks:
```bash
poetry run pre-commit run --all-files
```

## 🛠 Available Tasks
[Poe the Poet](https://github.com/nat-n/poethepoet) is used to define common development tasks.

You can list available tasks using:
```bash
poetry run poe --help
```

### Defined Tasks
| Task       | Description                                  |
|------------|----------------------------------------------|
| `lint`     | Runs `ruff` to lint and auto-fix code        |
| `typecheck`| Runs `mypy` for static type checking         |
| `check`    | Runs both `lint` and `typecheck`             |

Run a task like:
```bash
poetry run poe check
```

## 📝 License
This repository is licensed under the Apache License, Version 2.0. See the `LICENSE` file for details.
