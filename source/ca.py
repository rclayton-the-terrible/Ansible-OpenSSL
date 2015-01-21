import os, shutil
from subprocess import call

KEY_STENGTH = 2048
DAYS_VALID  = 3653 # ~10 years
TMPL_CA_CERT = "openssl req -x509 -config openssl.cnf -newkey rsa:{0} -days {1} -out cacert.pem -outform PEM -subj \"{2}\" -nodes"
TMPL_CONVERT = "openssl x509 -in cacert.pem -out cacert.cer -outform DER"
DEV_NULL = open('/dev/null', 'w')

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

    def __init__(self, cadir, subj):
        self.cadir = self.normalize_directory_path(cadir)
        self.subj = subj

    def normalize_directory_path(self, path):
        if path.endswith(os.sep):
            return path[:-1]
        else:
            return path

    def create_dir_if_not_exist(self, dir):
        if not os.path.exists(dir):
            try:
                os.mkdir(dir)
            except Exception as e:
                return dict(success=False, msg=e)
        return dict(success=True)

    def execute_command(self, cmd):
        call(cmd, shell=True, stdout=DEV_NULL, stderr=DEV_NULL)

    def validate_setup(self):
        certDirValid = self.create_dir_if_not_exist(self.cadir)
        if not certDirValid["success"]:
            return certDirValid
        elif not "CN=" in self.subj:
            return dict(success=False, msg="Common Name (CN) not found in subject string.")
        else:
            return dict(success=True)

    def setup(self):
        changed = False
        changes = []

        CURDIR = os.getcwd()

        os.chdir(self.cadir)

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
            self.execute_command(cmd)
            changes.append("Created CA certificate.")
            changed = True

        fileCaDerCert = "cacert.cer"

        if not os.path.exists(fileCaDerCert):
            cmd = TMPL_CONVERT
            self.execute_command(cmd)
            changes.append("Converted CA certificate to DER format.")
            changed = True

        os.chdir(CURDIR)

        return dict(success=True, changed=changed, changes=changes)

    def removeCA(self):

        if os.path.exists(self.cadir):
            shutil.rmtree(self.cadir)
            return dict(success=True, changed=True, changes=["Directory '{0}' removed".format(self.cadir)])
        else:
            return dict(success=True, changed=False, changes=[], msg="CA directory '{0}' does not exist.".format(self.cadir))


