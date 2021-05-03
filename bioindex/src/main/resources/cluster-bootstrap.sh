#!/bin/bash -xe

sudo yum install -y git

# need to upgrade pip
sudo python3 -m pip install --upgrade pip

# upgrading pip moves it to a location root doesn't have in its PATH
sudo ln -s /usr/local/bin/pip /bin/pip
sudo ln -s /usr/local/bin/pip3 /bin/pip3

# bioindex to get access to shared library functions
sudo pip3 install git+git://github.com/broadinstitute/dig-bioindex.git@master#egg=bioindex

# other python libs used by various stages
sudo pip3 install matplotlib
sudo pip3 install pandas
sudo pip3 install statsmodels
