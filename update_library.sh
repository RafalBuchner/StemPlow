# #!/bin/bash

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