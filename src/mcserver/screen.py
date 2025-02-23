import re
import subprocess
from pathlib import Path

SCREEN_PATTERN = re.compile(r"(?P<pid>[0-9]+)\.(?P<name>[a-z]+)")


def screen_exists(name: str, pwd: Path = Path.cwd()) -> bool:
    query = subprocess.run(
        "screen -list", capture_output=True, shell=True, cwd=pwd, check=False
    )
    return any(
        screen.group("name") == name
        for screen in SCREEN_PATTERN.finditer(query.stdout.decode())
    )


def create_screen(name: str, pwd: Path = Path.cwd()) -> None:
    subprocess.run(f"screen -dmS {name}", shell=True, cwd=pwd, check=False)


def execute_in_screen(name: str, command: str, pwd: Path = Path.cwd()) -> None:
    subprocess.Popen(f"screen -S {name} -X exec " + command, shell=True, cwd=pwd)
