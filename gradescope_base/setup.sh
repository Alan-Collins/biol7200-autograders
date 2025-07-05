#!/usr/bin/env bash

# make_assignment.sh will replace the lines below, DO NOT REMOVE
REPLACE_GITHUB_BRANCH

cd /autograder/source

apt-get install -y python3 python3-pip python3-dev

mkdir -p /root/.ssh
cp ssh_config /root/.ssh/config
# Make sure to include your private key here
cp deploy_key /root/.ssh/deploy_key
chmod 400 /root/.ssh/deploy_key
# To prevent host key verification errors at runtime
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

# Clone autograder files
git clone -b $GITHUB_BRANCH git@github.com:Alan-Collins/biol7200-autograders.git /autograder/biol7200-autograders
# Install python dependencies
pip3 install -r /autograder/biol7200-autograders/requirements.txt

# Depdendencies
mkdir /building
cd /building
wget \
    https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.16.0+-x64-linux.tar.gz \
    https://github.com/samtools/samtools/releases/download/1.22/samtools-1.22.tar.bz2

tar -zxf ncbi-blast-2.16.0+-x64-linux.tar.gz
tar -jxf samtools-1.22.tar.bz2

cd samtools-1.22/
./configure --prefix=/building/samtools && make && make install

cd ..
git clone https://github.com/lh3/seqtk.git
cd seqtk
make

cd ..
git clone https://github.com/lh3/minimap2.git
cd minimap2
make

cp \
    /building/ncbi-blast-2.16.0+/bin/* \
    /building/samtools/bin/samtools \
    /building/seqtk/seqtk \
    /building/minimap2/minimap2 \
    /usr/bin/

cd && rm -rf /building