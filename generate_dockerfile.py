#!/usr/bin/env python3
"""Generate a Dockerfile from local project metadata using an Ollama model."""
import argparse
import json
import subprocess
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

MANIFESTS = ("package.json", "requirements.txt", "pyproject.toml", "go.mod", "pom.xml", "Cargo.toml")


def collect_context(project: Path) -> str:
    files = []
    for name in MANIFESTS:
        path = project / name
        if path.exists():
            files.append(f"--- {name} ---\n{path.read_text(errors='replace')[:6000]}")
    source_names = [path.name for path in project.iterdir() if path.is_file()][:30]
    return f"Project files: {', '.join(source_names)}\n\n" + "\n\n".join(files)


def generate(model: str, context: str) -> str:
    prompt = f"""Generate only a complete Dockerfile for this project. Do not use markdown fences.
Use a small production base image, multi-stage builds where appropriate, a non-root user,
and an explicit CMD. Do not copy secrets. Project context:

{context}"""
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    request = Request("http://localhost:11434/api/generate", data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read())["response"].strip()
    except URLError as error:
        raise SystemExit("Ollama is unavailable. Start it with `ollama serve` and pull the requested model.") from error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--model", default="llama3.2")
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    project = args.project.resolve()
    if not project.is_dir():
        raise SystemExit(f"Not a directory: {project}")
    dockerfile = generate(args.model, collect_context(project))
    output = project / "Dockerfile.generated"
    output.write_text(dockerfile + "\n")
    print(f"Wrote {output}")
    if args.build:
        subprocess.run(["docker", "build", "-f", str(output), "-t", f"generated-{project.name}:local", str(project)], check=True)


if __name__ == "__main__":
    main()
