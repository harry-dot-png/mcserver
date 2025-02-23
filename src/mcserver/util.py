from pathlib import Path

import requests

def download(url: str, name: str, location: Path = Path.cwd()) -> Path:
    """Download a file from a URL."""
    filename = location / name

    session = requests.Session()
    with session.get(url, stream=True) as response:
        response.raise_for_status()
        with filename.open('wb') as file:
            for chunk in response.iter_content(chunk_size=None):
                file.write(chunk)
    return filename

def comparable_version(version: str) -> str:
    components = version.split(".")
    major = int(components[0])
    minor = int(components[1])
    patch = int(components[2]) if len(components) > 2 else 0

    return f"{major:04d}{minor:04d}{patch:04d}"
