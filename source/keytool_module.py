#!/usr/bin/python
# -*- coding: utf-8 -*-

from keytool import Keytool

def main():

    BASE_MODULE_ARGS = dict(
        cadir = dict(default="/etc/certs"),
        certname = dict(required=True),
        store_password = dict(required=True),
        hosts_to_trust = dict(required=True, type="list"),
        state = dict(default="present", choices=["present", "absent"])
    )

    module = AnsibleModule(
        argument_spec= BASE_MODULE_ARGS,
        supports_check_mode=True
    )

    keytool = Keytool(
        module.params["cadir"],
        module.params["certname"],
        module.params["store_password"],
        module.params["hosts_to_trust"]
    )

    isValid = keytool.validate()

    if isValid["success"]:
        if module.params["state"] == "present":
            isValid = keytool.build_trust_store()
        else:
            isValid = keytool.remove_trust_store()

    if not isValid["success"]:
        module.fail_json(msg=isValid["msg"])
    else:
        module.exit_json(**isValid)


# this is magic, see lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>
main()
