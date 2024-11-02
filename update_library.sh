# #!/bin/bash

# Download the specific folder from GitHub
git clone --depth 1 --filter=blob:none --sparse https://github.com/RafalBuchner/stemmath.git
cd stemmath
git sparse-checkout set stemmath

version=$(curl -s https://raw.githubusercontent.com/RafalBuchner/stemmath/main/pyproject.toml | grep '^version' | cut -d '"' -f2)

# Move the downloaded folder to the destination directory
rm -rf ../rb/mat/stemmath
mv stemmath ../rb/mat/

# Clean up
cd ..
rm -rf stemmath

echo "Folder downloaded and moved to source/code/stemPlow"

# Extract version number from pyproject.toml


echo $version
# Insert version number at the 11th line of __init__.py
# echo "__version__ = '$version'" >> $PWD/rb/mat/stemmath/__init__.py

sed -i '' '11i\
__version__ = "'$version'"
' $PWD/rb/mat/stemmath/__init__.py
