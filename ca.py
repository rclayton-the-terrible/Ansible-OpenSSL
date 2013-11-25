#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from subprocess import call

KEY_STENGTH = 2048
DAYS_VALID  = 3653 # ~10 years
TMPL_CA_CERT = "openssl req -x509 -config openssl.cnf -newkey rsa:{} -days {} -out cacert.pem -outform PEM -subj {} -nodes"
TMPL_CONVERT = "openssl x509 -in cacert.pem -out cacert.cer -outform DER"

OPENSSL_CNF = """
[ ca ]
default_ca = ca

[ ca ]
dir = .
certificate = $dir/cacert.pem
database = $dir/index.txt
new_certs_dir = $dir/certs
private_key = $dir/private/cakey.pem
serial = $dir/serial

default_crl_days = 7
default_days = 365
default_md = sha1

policy = ca_policy
x509_extensions = certificate_extensions

[ ca_policy ]
commonName = supplied
stateOrProvinceName = optional
countryName = optional
emailAddress = optional
organizationName = optional
organizationalUnitName = optional

[ certificate_extensions ]
basicConstraints = CA:false

[ req ]
default_bits = 2048
default_keyfile = ./private/cakey.pem
default_md = sha1
prompt = yes
distinguished_name = root_ca_distinguished_name
x509_extensions = root_ca_extensions

[ root_ca_distinguished_name ]
commonName = hostname

[ root_ca_extensions ]
basicConstraints = CA:true
keyUsage = keyCertSign, cRLSign

[ client_ca_extensions ]
basicConstraints = CA:false
keyUsage = digitalSignature
extendedKeyUsage = 1.3.6.1.5.5.7.3.2

[ server_ca_extensions ]
basicConstraints = CA:false
keyUsage = keyEncipherment
extendedKeyUsage = 1.3.6.1.5.5.7.3.1
"""

class CA:

    def __init__(self, certdir, subj):
        self.certdir = self.normalizeDirectoryPath(certdir)
        self.subj = subj

    def normalizeDirectoryPath(self, path):
        if path.endswith(os.sep):
            return path[:-1]
        else:
            return path

    def createDirIfNotExist(self, dir):
        if not os.path.exists(dir):
            try:
                os.mkdir(dir)
            except Exception as e:
                return dict(success=False, msg=e)
        return dict(success=True)

    def validateSetup(self):
        certDirValid = self.createDirIfNotExist(self.certdir)
        if not certDirValid["success"]:
            return certDirValid
        elif not "CN=" in self.subj:
            return dict(success=False, msg="Common Name (CN) not found in subject string.")
        else:
            return dict(success=True)

    def setup(self):
        changed = False
        changes = []

        os.chdir(self.certdir)

        fileOpensslCnf = "openssl.cnf"

        if not os.path.exists(fileOpensslCnf):
            opensslCnf = open(fileOpensslCnf, "w")
            opensslCnf.write(OPENSSL_CNF)
            opensslCnf.close()
            changes.append("Wrote openssl.cnf file.")
            changed = True

        dirPrivate = "private"

        if not os.path.exists(dirPrivate):
            os.mkdir(dirPrivate, 0700)
            changes.append("Created private directory.")
            changed = True

        dirCerts = "certs"

        if not os.path.exists(dirCerts):
            os.mkdir(dirCerts)
            changes.append("Created certs directory.")
            changed = True

        fileSerial = "serial"

        if not os.path.exists(fileSerial):
            serial = open(fileSerial, "w")
            serial.write("01")
            serial.close()
            changes.append("Created serial file.")
            changed = True

        fileIndexTxt = "index.txt"

        if not os.path.exists(fileIndexTxt):
            with file(fileIndexTxt, "a"):
                os.utime(fileIndexTxt, None)
            changes.append("Created index.txt file")
            changed = True

        fileCaCert = "cacert.pem"

        if not os.path.exists(fileCaCert):
            cmd = TMPL_CA_CERT.format(KEY_STENGTH, DAYS_VALID, self.subj)
            call(cmd, shell=True)
            changes.append("Created CA certificate.")
            changed = True

        fileCaDerCert = "cacert.cer"

        if not os.path.exists(fileCaDerCert):
            cmd = TMPL_CONVERT
            call(cmd, shell=True)
            changes.append("Converted CA certificate to DER format.")
            changed = True

        return dict(success=True, changed=changed, changes=changes)


def main():

    KARAF_BASE_MODULE_ARGS = dict(
        certdir = dict(default="/etc/certs"),
        subj = dict(default="/DC=com/DC=example/CN=CA/")
    )

    module = AnsibleModule(
        argument_spec= KARAF_BASE_MODULE_ARGS,
        supports_check_mode=True
    )

    ca = CA(module.params["certdir"], module.params["subj"])

    isValid = ca.validate()

    if isValid.success:
        isValid = ca.setup()

    if not isValid.success:
        module.fail_json(msg=isValid.msg)
    else:
        module.exit_json(**isValid)


# this is magic, see lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>
main()