"""Main script for mcserver."""

import argparse
from pathlib import Path

from mcserver.paper import (
    download_jar,
    get_latest_jarname,
    latest_jarname,
    startup_sh,
)
from mcserver.screen import create_screen, execute_in_screen, screen_exists


def main() -> None:  # noqa: D103
    parser = argparse.ArgumentParser(
        "Minecraft Paper Server",
        description=(
            "Python API for starting and updating a Minecraft server using Paper."
        ),
    )
    parser.add_argument(
        "command",
        help="Command to execute. Currently, only 'start' supported.",
        type=str,
    )
    parser.add_argument(
        "--update",
        help="Whether to update the server to the latest version.",
        action="store_true",
    )
    parser.add_argument(
        "--allow-experimental",
        help="Whether to allow experimental Paper builds.",
        action="store_true",
    )
    parser.add_argument(
        "--root",
        help=(
            "Root directory where the Paper server jar is located. Defaults to the "
            "current working directory."
        ),
        type=Path,
        default=Path.cwd(),
    )

    args = parser.parse_args()

    if args.command != "start":
        return

    root: Path = args.root.resolve()

    # Grab a Paper jar
    try:
        # Locate current Paper jar
        jar = next(root.glob("paper-*.jar"))
    except StopIteration:
        # Need to download a new Paper jar
        jarname = get_latest_jarname(allow_experimental=args.allow_experimental)
        jar = download_jar(jarname, root)

    # Update Paper jar if needed
    if args.update:
        jarname = latest_jarname(jar.name, allow_experimental=args.allow_experimental)

        if jarname != jar.name:
            # Delete old Paper jar
            jar.unlink()
            # Download new Paper jar
            jar = download_jar(jarname, root)

    # Generate start script
    startup = startup_sh(jar)

    if not screen_exists("minecraft"):
        # Create the "minecraft" screen
        create_screen("minecraft", pwd=root)

    # Start the server on the "minecraft" screen
    execute_in_screen("minecraft", startup.as_posix(), pwd=root)

    if not screen_exists("playit"):
        # Create the "playit" screen
        create_screen("playit", pwd=root)
        # Start playit on the "playit" screen
        # This only needs to happen when starting the screen for the
        # first time
        execute_in_screen("playit", "/usr/local/bin/playit start", pwd=root)

    return
