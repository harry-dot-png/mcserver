from pathlib import Path

import requests

from mcserver.util import comparable_version, download

START_PAPER_SH_TEMPLATE = (
    Path(__file__).parent / "resources" / "start-paper.sh.template"
)


def get_latest_version() -> str:
    """Get the latest stable Paper jar version."""
    with requests.get("https://api.papermc.io/v2/projects/paper") as response:
        response.raise_for_status()
        data = response.json()
    return data["versions"][-1]


def get_latest_stable_version_and_build() -> tuple[str, str]:
    """Get the latest stable Paper jar version and build number."""
    version = get_latest_version()
    with requests.get(
        f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds"
    ) as response:
        data = response.json()

    stables = [
        build["build"] for build in data["builds"] if build["channel"] == "default"
    ]
    return version, str(stables[-1])


def get_jar_version_and_build(name: str) -> tuple[str, str]:
    """Get the version and build number from a Paper jar filename."""
    return tuple(name.rsplit(".", 1)[0].split("-")[1:])


def get_latest_stable_jarname() -> str:
    """Get the filename of the latest stable Paper jar."""
    version, build = get_latest_stable_version_and_build()
    return f"paper-{version}-{build}.jar"


def download_jar(name: str, location: Path) -> Path:
    """Download a Paper jar given its filename."""
    version, build = get_jar_version_and_build(name)
    url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build}/downloads/{name}"
    return download(url, name=name, location=location)


def latest_jarname(old_name: str) -> str:
    """The latest Paper jar. Will request the Paper API to verify."""
    new_name = get_latest_stable_jarname()
    old_version, old_build = get_jar_version_and_build(old_name)
    new_version, new_build = get_jar_version_and_build(new_name)
    return (
        new_name
        if comparable_version(new_version) > comparable_version(old_version)
        and new_build > old_build
        else old_name
    )


def startup_sh(server_jar: Path) -> Path:
    with START_PAPER_SH_TEMPLATE.open() as template:
        script = template.read()

    script_path: Path = server_jar.parent / "start-paper.sh"
    with script_path.open("w") as script_file:
        script_file.write(script.replace("$JARNAME$", server_jar.name))
    return script_path
