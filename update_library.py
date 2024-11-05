import requests
from git import Repo
from pathlib import Path
import shutil
import tomllib

rootDir = Path(
    Repo(Path.cwd(), search_parent_directories=True).git.rev_parse("--show-toplevel")
)

stemmathRepoDir = rootDir / "stemmath"

if stemmathRepoDir.exists():
    shutil.rmtree(stemmathRepoDir)
# Clone the specific folder from GitHub
repo = Repo.clone_from(
    "https://github.com/RafalBuchner/stemmath.git",
    "stemmath",
    depth=1,
    filter="blob:none",
)
repo.git.sparse_checkout("set", "stemmath")

# Extract version number from pyproject.toml
response = requests.get(
    "https://raw.githubusercontent.com/RafalBuchner/stemmath/main/pyproject.toml"
)


# Parse the version from the pyproject.toml content
pyproject_data = tomllib.loads(response.text)
version = pyproject_data["tool"]["poetry"]["version"]

# Move the downloaded folder to the destination directory
destination_dir = rootDir / "source/code/stemPlow/stemmath"
if destination_dir.exists():
    shutil.rmtree(destination_dir)
destination_dir.parent.mkdir(parents=True, exist_ok=True)
shutil.move(stemmathRepoDir / "stemmath", destination_dir)

# Clean up
shutil.rmtree("stemmath")

print("Folder downloaded and moved to source/code/stemPlow")

# Insert version number at the 11th line of __init__.py
init_file_path = destination_dir / "__init__.py"
with init_file_path.open("r") as file:
    lines = file.readlines()

lines.insert(17, f'__version__ = "{version}"\n')

with init_file_path.open("w") as file:
    file.writelines(lines)
