
from subprocess import call
import os

TMPL_GEN_TS = "keytool -import -noprompt -alias {0} -file {1} -keystore {2} -storepass:file {3}.storepass"
DEV_NULL = open('/dev/null', 'w')

class Keytool:


    def __init__(self, cadir, hostname, store_password, hosts_to_trust):

        self.cadir = cadir
        self.hostname = hostname
        self.store_password = store_password
        self.hosts_to_trust = hosts_to_trust

    def execute_command(self, cmd):
        call(cmd, shell=True, stdout=DEV_NULL, stderr=DEV_NULL)

    def validate(self):

        if not os.path.exists(self.cadir):
            return dict(success=False, msg="CA directory '{0}' does not exist.".format(self.cadir))
        elif len(self.hosts_to_trust) == 0:
            return dict(success=False, msg="No hosts specified for the truststore.")
        else:
            return dict(success=True)

    def ensure_directory_exists(self, dir):
        if not os.path.exists(dir):
            os.mkdir(dir)

    def get_truststore_path(self):
        return "truststores" + os.sep + self.hostname + ".trust.jks"

    def get_storepass_path(self):
        return self.hostname + ".storepass"

    def resolve_certificate(self, host):
        server = "./server/{0}.cert.pem".format(host)
        client = "./client/{0}.cert.pem".format(host)
        if os.path.exists(server):
            return server
        elif os.path.exists(client):
            return client
        else:
            return None

    def build_trust_store(self):

        changed = False
        success = True
        errors = []
        changes = []

        CURDIR = os.getcwd()

        os.chdir(self.cadir)

        self.ensure_directory_exists("truststores")

        truststore_path = self.get_truststore_path()
        storepass_path = self.get_storepass_path()

        if not os.path.exists(truststore_path):

            # Write the password out to file.
            with open(storepass_path, "w") as storepass:
                storepass.write(self.store_password)

            try:

                cmd = TMPL_GEN_TS.format("CA", "cacert.pem", truststore_path, self.hostname)
                self.execute_command(cmd)
                changed = True
                changes.append("Added the CA Certificate to the truststore.")

                for host in self.hosts_to_trust:

                    hostcert = self.resolve_certificate(host)

                    if not hostcert is None:
                        cmd = TMPL_GEN_TS.format(host, hostcert, truststore_path, self.hostname)
                        changes.append("Executing: '{0}'".format(cmd))
                        self.execute_command(cmd)
                        changed = True
                        changes.append("Added '{0}' to the truststore.".format(host))
                    else:
                        success=False
                        errors.append("Could not find cert for host: {0}".format(host))

            except Exception as e:
                success = False
                errors.append(e.message)

            finally:

                # Remove the password
                os.remove(storepass_path)

        if success == False:
            os.remove(truststore_path)

        os.chdir(CURDIR)

        return dict(success=success, changed=changed, changes=changes, path=truststore_path, errors=errors, msg=", ".join(errors))


    def remove_trust_store(self):

        changed = False
        changes = []

        CURDIR = os.getcwd()

        os.chdir(self.cadir)

        truststore_path = self.get_truststore_path()

        if os.path.exists(truststore_path):
            os.remove(truststore_path)
            changed=True
            changes.append("Successfully removed truststore.")

        os.chdir(CURDIR)

        return dict(success=True, changed=changed, changes=changes, msg="")


