#!/bin/bash

#################################################################################################
# Sync the source files with your Ansible module directory.  Check permissions!  You may need to
# use "sudo" or "chown" or "chmod" to run this script!
#################################################################################################

if [ ! -d /usr/share/ansible/openssl/ ];
then
    mkdir /usr/share/ansible/openssl/
fi

# Clear the current scripts
rm /usr/share/ansible/openssl/*

# Copy the new ones
cp dist/* /usr/share/ansible/openssl/