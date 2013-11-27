#!/bin/bash

#################################################################################################
# Conveniently runs the build script in the "source" directory, which will compose the Ansible
# modules with the library modules (split for testing purposes).
#################################################################################################

if [ ! -d dist ];
then
    mkdir dist
fi

cd source


python build.py