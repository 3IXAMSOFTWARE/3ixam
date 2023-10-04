#!/bin/sh

# This shell script checks out and compiles ixam, tested on ubuntu 10.04
# assumes you have dependencies installed already

# See this page for more info:
#   https://wiki.ixam.org/wiki/Building_Ixam/Linux/Generic_Distro/CMake

# grab ixam
mkdir ~/ixam-git
cd ~/ixam-git

git clone http://git.ixam.org/ixam.git
cd ixam
git submodule update --init --recursive
git submodule foreach git checkout master
git submodule foreach git pull --rebase origin master

# create build dir
mkdir ~/ixam-git/build-cmake
cd ~/ixam-git/build-cmake

# cmake without copying files for fast rebuilds
# the files from git will be used in place
cmake ../ixam

# make ixam, will take some time
make -j$(nproc)

# link the binary to ixams source directory to run quickly
ln -s ~/ixam-git/build-cmake/bin/ixam ~/ixam-git/ixam/ixam.bin

# useful info
echo ""
echo "* Useful Commands *"
echo "   Run 3IXAM: ~/ixam-git/ixam/ixam.bin"
echo "   Update 3IXAM: git pull --rebase; git submodule foreach git pull --rebase origin master"
echo "   Reconfigure 3IXAM: cd ~/ixam-git/build-cmake ; cmake ."
echo "   Build 3IXAM: cd ~/ixam-git/build-cmake ; make"
echo ""
