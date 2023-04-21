#!/bin/bash
# originally from https://github.com/ChrisTheCoolHut/PinCTF/blob/master/installPin.sh

WORKDIR=$(pwd)

#Pull latest from https://software.intel.com/en-us/articles/pin-a-binary-instrumentation-tool-downloads

URL=https://software.intel.com/sites/landingpage/pintool/downloads/pin-3.11-97998-g7ecce2dac-gcc-linux.tar.gz

wget $URL -O pin.tar.gz 

tar -xvf pin.tar.gz
rm pin.tar.gz

#Install Ubuntu Dependencies
sudo apt-get install gcc-multilib g++-multilib libc6-dev-i386

#Rename pin directory
mv pin-* pin

cd pin/source/tools/ManualExamples/

#Build for both 32 and 64 bit
make inscount1.test TARGET=ia32
make inscount1.test