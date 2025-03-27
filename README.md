# MCP Code Agent With OpenAI LLMs
[![Python Version](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3110/) [![MCP Version](https://img.shields.io/badge/MCP-1.5.0-orange?logo=anthropic&logoColor=white)](https://pypi.org/project/mcp/) [![OpenAI Version](https://img.shields.io/badge/OpenAI-1.68.2-lightgrey?logo=openai&logoColor=whit)](https://pypi.org/project/openai/)

## 📘 Overview
This project implements AI agent with the use of OpenAI LLMs that is designed to interact with the MCP framework and.

## 📦 Installation
First, ensure you have [Poetry installed](https://python-poetry.org/docs/#installation).

```bash
poetry install
```
## 🚀 Running the Project

1. **Ensure Docker is Running**
   Make sure the Docker daemon is active on your system. You can check this by running:
   ```bash
   docker info
   ```
   If Docker is not installed, follow the [official Docker installation guide](https://docs.docker.com/get-docker/) for your operating system.

2. **Start the MCP Weather Server**
   Launch the weather server using:
   ```bash
   poetry run poe weather_server
   ```

3. **Run the Chainlit Application**
   Start the Chainlit app with:
   ```bash
   poetry run poe app
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
| `app`    | Runs the Chainlit application             |

Run a task like:
```bash
poetry run poe check
```

## 📝 License
This repository is licensed under the Apache License, Version 2.0. See the `LICENSE` file for details.
