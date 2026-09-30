# Dockerfile Generator with Local LLMs

Generate a production-minded Dockerfile from a source repository using Ollama. The tool inspects common project manifests, asks a local model for a Dockerfile, then can optionally build it.

## Prerequisites

- Python 3.10+
- Docker
- Ollama with a local model, for example: `ollama pull llama3.2`

## Run

```bash
python3 generate_dockerfile.py /path/to/project --model llama3.2
python3 generate_dockerfile.py /path/to/project --model llama3.2 --build
```

The script writes `Dockerfile.generated` into the target project. Review generated files before building or deploying them.

## What it demonstrates

- Local LLM inference through Ollama's HTTP API
- Deterministic repository context extraction
- Prompt constraints for non-root, multi-stage Docker builds
- Optional Docker build validation
