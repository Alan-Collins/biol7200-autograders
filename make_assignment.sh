#!/usr/bin/env bash
GITHUB_BRANCH=$(git branch --show-current)

# delete previous files if any
rm $GITHUB_BRANCH.zip

# copy all files necessary for assignment
# make sure you have copied your deploy key to gradescope_base/
mkdir -p zip_$GITHUB_BRANCH
cp gradescope_base/* zip_$GITHUB_BRANCH/

sed -i "s,REPLACE_GITHUB_BRANCH,GITHUB_BRANCH=$GITHUB_BRANCH," zip_$name/setup.sh

# zip the assignement and delete folder
zip -r -m -j $name.zip zip_$name/*
rmdir zip_$name


