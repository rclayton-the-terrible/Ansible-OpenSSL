import os, shutil

BUILD_DIR = "../dist"

FILES_TO_BUILD = [
    { "file": "ca", "module": "ca_module.py", "library": "ca.py", "import": "from ca import CA" },
    { "file": "certificate", "module": "certificate_module.py", "library": "certificate.py", "import": "from certificate import Certificate" },
    { "file": "keytool", "module": "keytool_module.py", "library": "keytool.py", "import": "from keytool import Keytool" }
]

def read_file(filename):
    with open(filename, "r") as f:
        return f.read()

def delete_old_build_file(filename):
    file = BUILD_DIR + os.sep + filename
    if os.path.exists(file):
        os.remove(file)

def replace_import(filename, ansibleModule, importStatement, libraryToInsert):
    fileToExport = BUILD_DIR + os.sep + filename
    moduleSrc = read_file(ansibleModule)
    librarySrc = read_file(libraryToInsert)
    compiledSrc = moduleSrc.replace(importStatement, librarySrc)
    destination = open(fileToExport, "w")
    destination.write(compiledSrc)
    destination.close()

for file_config in FILES_TO_BUILD:
    print "Building file {0}.".format(file_config["file"])
    delete_old_build_file(file_config["file"])
    replace_import(file_config["file"], file_config["module"], file_config["import"], file_config["library"])
