import subprocess
from pathlib import Path

def screen_exists(name: str) -> bool: ...

def create_screen(name: str, pwd: Path = Path.cwd()) -> None:
    subprocess.run(f"screen -dmS {name}", shell=True, cwd=pwd)

def execute_in_screen(name: str, command: str, pwd: Path = Path.cwd()) -> None:
    subprocess.Popen(f"screen -S {name} -X exec " + command, shell=True, cwd=pwd)