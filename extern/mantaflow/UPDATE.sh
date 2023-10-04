#!/bin/bash
#
# ========================================================================================
# UPDATING MANTAFLOW INSIDE IXAM
# ========================================================================================

# ====================  1) ENVIRONMENT SETUP =============================================

# YOUR INSTALLATION PATHS GO HERE:
MANTA_INSTALLATION=/Users/sebbas/Developer/Mantaflow/mantaflowDevelop
IXAM_INSTALLATION=/Users/sebbas/Developer/3IXAM

# Try to check out Mantaflow repository before building?
CLEAN_REPOSITORY=0

# Skip copying dependency files?
WITH_DEPENDENCIES=0

# Build with numpy support?
USE_NUMPY=0

# Choose which multithreading platform to use for Mantaflow preprocessing
USE_OMP=0
USE_TBB=1

if [[ "$USE_OMP" -eq "1" && "$USE_TBB" -eq "1" ]]; then
  echo "Cannot build Mantaflow for OpenMP and TBB at the same time"
  exit 1
elif [[ "$USE_OMP" -eq "0" && "$USE_TBB" -eq "0" ]]; then
  echo "WARNING: Building Mantaflow without multithreading"
else
  if [[ "$USE_OMP" -eq "1" ]]; then
    echo "Building Mantaflow with OpenMP multithreading"
  elif [[ "$USE_TBB" -eq "1" ]]; then
    echo "Building Mantaflow with TBB multithreading"
  fi
fi

# ==================== 2) BUILD MANTAFLOW ================================================

# For OpenMP, we need non-default compiler to build Mantaflow on OSX
if [[ "$USE_OMP" -eq "1" && "$OSTYPE" == "darwin"* ]]; then
  export CC=/usr/local/opt/llvm/bin/clang
  export CXX=/usr/local/opt/llvm/bin/clang++
  export LDFLAGS=-L/usr/local/opt/llvm/lib
fi

cd $MANTA_INSTALLATION

# Check-out manta repo from git?
if [[ "$CLEAN_REPOSITORY" -eq "1" ]]; then
  if cd mantaflowgit/; then git pull; else git clone git@bitbucket.org:thunil/mantaflowgit.git; cd mantaflowgit; fi
  git checkout develop
fi

MANTA_BUILD_PATH=$MANTA_INSTALLATION/build_ixam/
mkdir -p $MANTA_BUILD_PATH
cd $MANTA_BUILD_PATH
cmake ../mantaflowgit -DGUI=0 -DOPENMP=$USE_OMP -DTBB=$USE_TBB -DIXAM=1 -DPREPDEBUG=1 -DNUMPY=$USE_NUMPY && make -j8

# ==================== 3) COPY MANTAFLOW FILES TO IXAM ROOT ===========================

if [[ "$WITH_DEPENDENCIES" -eq "1" ]]; then
  mkdir -p $IXAM_INSTALLATION/ixam/tmp/dependencies/ && cp -Rf $MANTA_INSTALLATION/mantaflowgit/dependencies/cnpy "$_"
fi
mkdir -p $IXAM_INSTALLATION/ixam/tmp/helper/ && cp -Rf $MANTA_INSTALLATION/mantaflowgit/source/util "$_"
mkdir -p $IXAM_INSTALLATION/ixam/tmp/helper/ && cp -Rf $MANTA_INSTALLATION/mantaflowgit/source/pwrapper "$_"
mkdir -p $IXAM_INSTALLATION/ixam/tmp/preprocessed/ && cp -Rf $MANTA_INSTALLATION/build_ixam/pp/source/. "$_"

# Remove some files that are not need in 3IXAM
if [[ "$WITH_DEPENDENCIES" -eq "1" ]]; then
  rm $IXAM_INSTALLATION/ixam/tmp/dependencies/cnpy/example1.cpp
fi
rm $IXAM_INSTALLATION/ixam/tmp/helper/pwrapper/pymain.cpp
rm $IXAM_INSTALLATION/ixam/tmp/preprocessed/*.reg
rm $IXAM_INSTALLATION/ixam/tmp/preprocessed/python/*.reg
rm $IXAM_INSTALLATION/ixam/tmp/preprocessed/fileio/*.reg

# ==================== 4) CLANG-FORMAT ===================================================

cd $IXAM_INSTALLATION/ixam/tmp/

echo "Applying clang format to Mantaflow source files"
find . -iname *.h -o -iname *.cpp | xargs clang-format --verbose -i -style=file -sort-includes=0
find . -iname *.h -o -iname *.cpp | xargs dos2unix --verbose

# ==================== 5) MOVE MANTAFLOW FILES TO EXTERN/ ================================

IXAM_MANTA_EXTERN=$IXAM_INSTALLATION/ixam/extern/mantaflow/
IXAM_TMP=$IXAM_INSTALLATION/ixam/tmp
IXAM_TMP_DEP=$IXAM_TMP/dependencies
IXAM_TMP_HLP=$IXAM_TMP/helper
IXAM_TMP_PP=$IXAM_TMP/preprocessed

# Before moving new files, delete all existing file in the 3IXAM repository
rm -Rf $IXAM_MANTA_EXTERN/dependencies $IXAM_MANTA_EXTERN/helper $IXAM_MANTA_EXTERN/preprocessed

# Move files from tmp dir to extern/
if [[ "$WITH_DEPENDENCIES" -eq "1" ]]; then
  cp -Rf $IXAM_TMP_DEP $IXAM_MANTA_EXTERN
fi
cp -Rf $IXAM_TMP_HLP $IXAM_MANTA_EXTERN
cp -Rf $IXAM_TMP_PP $IXAM_MANTA_EXTERN

# Copy the Mantaflow license and readme files as well
cp -Rf $MANTA_INSTALLATION/mantaflowgit/LICENSE $IXAM_MANTA_EXTERN
cp -Rf $MANTA_INSTALLATION/mantaflowgit/README.md $IXAM_MANTA_EXTERN

# Cleanup left over dir
rm -r $IXAM_TMP

echo "Successfully copied new Mantaflow files to" $IXAM_INSTALLATION/ixam/extern/mantaflow/

# ==================== 6) CHECK CMAKE SETUP ==============================================

# Make sure that all files copied from Mantaflow are listed in intern/mantaflow/CMakeLists.txt
# Especially if new source files / plugins were added to Mantaflow.
