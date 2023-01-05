#!/bin/bash -xe

# install needed python
sudo yum install -y python3-devel
sudo pip3 install -U Cython
sudo pip3 install -U pybind11
sudo pip3 install -U pythran
sudo pip3 install -U numpy
sudo pip3 install -U scipy --no-binary scipy
