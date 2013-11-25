import os, shutil

BUILD_DIR = ".."

FILES_TO_BUILD = [
    { "file": "ca.py", "module": "ca_module.py", "library": "ca.py", "import": "from ca import CA" },
    #{ "file": "", "module": "", "library": "", "import": "" },
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
    print "Building file {}.".format(file_config["file"])
    delete_old_build_file(file_config["file"])
    replace_import(file_config["file"], file_config["module"], file_config["import"], file_config["library"])
