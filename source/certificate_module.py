#!/usr/bin/python
# -*- coding: utf-8 -*-

from certificate import Certificate

def main():

    BASE_MODULE_ARGS = dict(
        cadir = dict(default="/etc/certs"),
        hostname = dict(required=True),
        subj = dict(default="/DC=com/DC=example/CN=CA/"),
        p12password = dict(required=True),
        certtype = dict(default="server", choices=["server", "client"]),
        state = dict(default="present", choices=["present", "absent"]),
        subjectAltNames = dict(required=False)
    )

    module = AnsibleModule(
        argument_spec= BASE_MODULE_ARGS,
        supports_check_mode=True
    )

    isServerCert = True

    if module.params["certtype"] == "client":
        isServerCert = False

    # cadir, hostname, subj, p12password, isServerCert
    cert = Certificate(
        module.params["cadir"],
        module.params["hostname"],
        module.params["subj"],
        module.params["p12password"],
        isServerCert,
        module.params["subjectAltNames"]
    )

    isValid = cert.validate_config()

    if isValid["success"]:
        if module.params["state"] == "present":
            isValid = cert.create_certificate()
        else:
            isValid = cert.remove_certificate()

    if not isValid["success"]:
        module.fail_json(msg=isValid["msg"])
    else:
        module.exit_json(**isValid)


# this is magic, see lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>
main()
