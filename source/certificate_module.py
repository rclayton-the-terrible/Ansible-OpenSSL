#!/usr/bin/python
# -*- coding: utf-8 -*-

from certificate import Certificate

def main():

    KARAF_BASE_MODULE_ARGS = dict(
        cadir = dict(default="/etc/certs"),
        hostname = dict(required=True),
        subj = dict(default="/DC=com/DC=example/CN=CA/"),
        p12password = dict(required=True),
        isServerCert = dict(default=True)
    )

    module = AnsibleModule(
        argument_spec= KARAF_BASE_MODULE_ARGS,
        supports_check_mode=True
    )

    # cadir, hostname, subj, p12password, isServerCert
    cert = Certificate(
        module.params["cadir"],
        module.params["hostname"],
        module.params["subj"],
        module.params["p12password"],
        module.params["isServerCert"]
    )

    isValid = cert.validate_config()

    if isValid.success:
        isValid = cert.createCertificate()

    if not isValid.success:
        module.fail_json(msg=isValid.msg)
    else:
        module.exit_json(**isValid)


# this is magic, see lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>
main()