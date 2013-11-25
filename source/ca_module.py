#!/usr/bin/python
# -*- coding: utf-8 -*-

from ca import CA

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