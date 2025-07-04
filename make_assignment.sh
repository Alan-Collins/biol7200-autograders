#!/usr/bin/env bash
GITHUB_BRANCH=$(git branch --show-current)

# delete previous files if any
rm $GITHUB_BRANCH.zip

# copy all files necessary for assignment
# make sure you have copied your deploy key to gradescope_base/
mkdir -p zip_$GITHUB_BRANCH
cp gradescope_base/* zip_$GITHUB_BRANCH/

sed -i "s,REPLACE_GITHUB_BRANCH,GITHUB_BRANCH=$GITHUB_BRANCH," zip_$GITHUB_BRANCH/setup.sh

# zip the assignement and delete folder
zip -r -m -j $GITHUB_BRANCH.zip zip_$GITHUB_BRANCH/*
rmdir zip_$GITHUB_BRANCH


