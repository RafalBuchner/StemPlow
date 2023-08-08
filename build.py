'''build RoboFont StemPlow Extension'''

import os
from mojo.extensions import ExtensionBundle

__version__ = "1.220"

def exec_cmd(cmd):
    import subprocess
    import shlex
    import traceback
    try:
        subprocess.check_call(shlex.split(cmd))
    except:
        print(f"issue with cmd\n\t${cmd}")
        print(traceback.format_exc())



# get current folder
basePath = os.path.dirname(__file__)

# source folder for all extension files
sourcePath = os.path.join(basePath, 'source')

# folder with python files
libPath = os.path.join(sourcePath, 'code')

# # folder with html files
# htmlPath = os.path.join(sourcePath, 'documentation')
htmlPath = None

# # folder with resources (icons etc)
# resourcesPath = os.path.join(sourcePath, 'resources')
resourcesPath = None

# load license text from file
# see choosealicense.com for more open-source licenses
licensePath = os.path.join(basePath, 'licence.txt')

# boolean indicating if only .pyc should be included
pycOnly = False

# name of the compiled extension file
extensionFile = 'StemPlow.roboFontExt'

# path of the compiled extension
buildPath = os.path.join(basePath, 'build')
extensionPath = os.path.join(buildPath, extensionFile)

# initiate the extension builder
B = ExtensionBundle()

# name of the extension
B.name = "StemPlow"

# name of the developer
B.developer = 'Rafał Buchner'

# URL of the developer
B.developerURL = 'http://github.com/rafalbuchner'

# # extension icon (file path or NSImage)
# imagePath = os.path.join(resourcesPath, 'icon.png')
# B.icon = imagePath

# version of the extension
B.version = __version__

# should the extension be launched at start-up?
B.launchAtStartUp = True

# script to be executed when RF starts
B.mainScript = 'StemPlowTool.py'

# does the extension contain html help files?
B.html = False

# minimum RoboFont version required for this extension
B.requiresVersionMajor = '4'
B.requiresVersionMinor = '2'

# scripts which should appear in Extensions menu
B.addToMenu = [
    {
        'path' : 'StemPlowSettings.py',
        'preferredName': '↔ Stem Plow Settings',
        'shortKey' : '',
    },

]

# license for the extension
with open(licensePath, encoding="utf-8") as license:
    B.license = license.read()

# # expiration date for trial extensions
# B.expireDate = '2019-12-31'

# compile and save the extension bundle
print(f'building extension {B.name} version {__version__}...', end=' ')
# B.save(extensionPath, libPath=libPath, htmlPath=htmlPath, resourcesPath=resourcesPath, pycOnly=["3.6", "3.7"])
B.save(extensionPath, libPath=libPath, htmlPath=htmlPath, resourcesPath=resourcesPath)
B.save(extensionPath, libPath=libPath, htmlPath=htmlPath, resourcesPath=resourcesPath)
print('done!')

# check for problems in the compiled extension
print()
print(B.validationErrors())
if "" == str(B.validationErrors()):
    B.install()
