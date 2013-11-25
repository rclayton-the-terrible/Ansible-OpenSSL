#!/bin/bash

if [ ! -d /usr/share/ansible/openssl/ ];
then
    mkdir /usr/share/ansible/openssl/
fi

// Clear the current scripts
rm /usr/share/ansible/openssl/*

// Copy the new ones
cp ./build/* /usr/share/ansible/openssl/