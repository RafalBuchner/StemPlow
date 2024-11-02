# #!/bin/bash

# # Define source and destination directories
# SOURCE_DIR="stemmath/stemmath"
# DEST_DIR="source/code/stemPlow"

# # Copy the folder
# cp -r "$SOURCE_DIR" "$DEST_DIR"

# echo "Folder copied from $SOURCE_DIR to $DEST_DIR"

# Download the specific folder from GitHub
git clone --depth 1 --filter=blob:none --sparse https://github.com/RafalBuchner/stemmath.git
cd stemmath
git sparse-checkout set stemmath

# Move the downloaded folder to the destination directory
mv stemmath ../source/code/stemPlow

# Clean up
cd ..
rm -rf stemmath

echo "Folder downloaded and moved to source/code/stemPlow"