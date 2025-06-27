"""Function for working with Paper."""

# ruff: noqa: S602, S113

import subprocess
from pathlib import Path

import requests

from mcserver.util import comparable_version

START_PAPER_SH_TEMPLATE = (
    Path(__file__).parent / "resources" / "start-paper.sh.template"
)

HEADERS = {}


def get_latest_version() -> str:
    """Get the latest supported version of Paper."""
    with requests.get("https://fill.papermc.io/v3/projects/paper/versions") as response:
        response.raise_for_status()
        data = response.json()

    for version in data["versions"]:
        if version["version"]["support"]["status"] != "SUPPORTED":
            continue
        return version["version"]["id"]

    msg = "Could not locate a supported version of Paper..."
    raise Exception(msg)  # noqa: TRY002


def get_latest_build() -> tuple[str, str]:
    """
    Return the latest Paper build. Returns the jar name and its download
    URL.
    """  # noqa: D205, D212
    version = get_latest_version()
    with requests.get(
        f"https://fill.papermc.io/v3/projects/paper/versions/{version}/builds/latest",
    ) as response:
        response.raise_for_status()
        data = response.json()

    return data["downloads"]["server:default"]["name"], data["downloads"][
        "server:default"
    ]["url"]


def get_jar_version_and_build(name: str) -> tuple[str, str]:
    """Get the version and build number from a Paper jar filename."""
    return tuple(name.rsplit(".", 1)[0].split("-")[1:])


def get_latest_jarname(old_name: str) -> tuple[str, str | None]:
    """
    Get the latest Paper jar. Requests the Paper API to verify. Also
    returns the download URL if there is a newer Paper jar.
    """  # noqa: D205, D212
    new_name, url = get_latest_build()
    old_version, old_build = get_jar_version_and_build(old_name)
    new_version, new_build = get_jar_version_and_build(new_name)
    return (
        (new_name, url)
        if comparable_version(new_version) > comparable_version(old_version)
        and new_build > old_build
        else (old_name, None)
    )


def startup_sh(server_jar: Path) -> Path:
    """Overwrite the startup script template with a new Paper.jar."""
    with START_PAPER_SH_TEMPLATE.open() as template:
        script = template.read()

    script_path: Path = server_jar.parent / "start-paper.sh"
    with script_path.open("w") as script_file:
        script_file.write(script.replace("$JARNAME$", server_jar.name))

    subprocess.run(f"chmod +x {script_path.as_posix()}", shell=True, check=False)

    return script_path
