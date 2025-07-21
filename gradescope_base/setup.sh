#!/usr/bin/env bash

# make_assignment.sh will replace the lines below, DO NOT REMOVE
REPLACE_GITHUB_BRANCH

cd /autograder/source

# dependencies for samtools build taken from staphb dockerfile plus python
apt-get update && apt-get install --no-install-recommends -y \
    libncurses5-dev \
    libbz2-dev \
    liblzma-dev \
    libcurl4-gnutls-dev \
    zlib1g-dev \
    libssl-dev \
    gcc \
    wget \
    make \
    perl \
    bzip2 \
    gnuplot \
    ca-certificates \
    gawk &&\
    apt-get autoclean && rm -rf /var/lib/apt/lists/*

mkdir -p /root/.ssh
cp ssh_config /root/.ssh/config
# Make sure to include your private key here
cp deploy_key /root/.ssh/deploy_key
chmod 400 /root/.ssh/deploy_key
# To prevent host key verification errors at runtime
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

# Install mamba for python version controlling
wget -q -O Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3.sh -b -p "${HOME}/conda"
source "${HOME}/conda/etc/profile.d/conda.sh"
# For mamba support also run the following command
source "${HOME}/conda/etc/profile.d/mamba.sh"
mamba shell init
source "${HOME}/.bashrc"
mamba create -y -n biol7200 python pip
mamba activate biol7200

# Clone autograder files
git clone -b $GITHUB_BRANCH git@github.com:Alan-Collins/biol7200-autograders.git /autograder/biol7200-autograders
# Install python dependencies
pip3 install -r /autograder/biol7200-autograders/requirements.txt

# Depdendencies
mkdir /building
cd /building
wget -q \
    https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.16.0/ncbi-blast-2.16.0+-x64-linux.tar.gz \
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
