#!/usr/bin/env bash

# CHANGE THESE FOR YOUR REPO!
GITHUB_REPO='git@github.com:Alan-Collins/biol7200-autograders.git'
REPO_NAME="biol7200-autograders"
GITHUB_BRANCH=$(git branch --show-current)


# input the assignment number and the file that students have to fill out
name=$1

# delete previous files if any
rm $name.zip

# copy all files necessary for assignment
# make sure you have copied your deploy key to gradescope_base/
mkdir -p zip_$name
cp gradescope_base/* zip_$name/

# add assignment name and solution filename to run_autograder
sed -i "s/REPLACE_NAME/NAME=$name/" zip_$name/run_autograder
sed -i "s/REPLACE_REPO_NAME/REPO_NAME=$REPO_NAME/" zip_$name/run_autograder

sed -i "s/REPLACE_REPO_NAME/REPO_NAME=$REPO_NAME/" zip_$name/setup.sh
sed -i "s,REPLACE_GITHUB_REPO,GITHUB_REPO=$GITHUB_REPO," zip_$name/setup.sh
sed -i "s,REPLACE_GITHUB_BRANCH,GITHUB_BRANCH=$GITHUB_BRANCH," zip_$name/setup.sh

# zip the assignement and delete folder
zip -r -m -j $name.zip zip_$name/*
rmdir zip_$name


