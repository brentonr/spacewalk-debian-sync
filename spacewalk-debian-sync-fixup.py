#!/usr/bin/python
import argparse
import os
import urlparse
import requests
import tempfile
import re
import bz2
import gzip

RHN_CACHE_ROOT = '/var/cache/rhn/repodata'

def setupParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--channel', required=True)
    return parser

def validateArgs(args):
    return

def downloadRemoteFile(url):
    remoteFile = urlparse.urljoin(url, 'Packages.bz2')
    r = requests.get(remoteFile)
    tempFile, tempFileName = tempfile.mkstemp()
    tempFile = os.fdopen(tempFile, 'r+b')
    tempFile.write(r.content)
    tempFile.close()
    tempFile = bz2.BZ2File(tempFileName)
    return (tempFile, tempFileName)

def parsePackage(file, initialLine):
    line = initialLine
    package = {}
    currKey = None
    while not re.match(r'^$', line):
        if line[-1] == '\n':
            line = line[0:-1]
        if (line[0] == ' '):
            package[currKey] = package[currKey] + '\n' + line
        else:
            m = re.match(r'^([^:]+): (.*)$', line)
            currKey = m.group(1)
            package[currKey] = m.group(2)
        line = file.readline()
    return package

def getPackage(file):
    line = ''
    while not re.match(r'^Package: .*$', line):
        line = file.readline()
        if not line:
            break

    if line:
        package = parsePackage(file, line)
    else:
        package = None

    return package

def findPackage(file, package):
    file.seek(0, 0)
    line = ''
    while not re.match(r'^Package: ' + package['Package'] + '$', line):
        line = file.readline()
        if not line:
            break

    if line:
        package = parsePackage(file, line)
    else:
        package = None

    return package

def writePackage(file, package):
    file.write('Package: ' + package['Package'] + '\n')
    del package['Package']
    for k,v in package.iteritems():
        file.write(k + ': ' + v + '\n')
    file.write('\n')

def replacePackagesFile(original, new):
    os.rename(original, original + '.bak')
    if original.endswith('.bz2'):
        dst = bz2.BZ2File(original, 'w+b')
    elif original.endswith('.gz'):
        dst = gzip.open(original, 'w+b')
    else:
        dst = open(original, 'w+b')

    src = open(new, 'r')

    dst.write(src.read())
    dst.close()
    src.close()

    os.remove(new)

def getLocalPackages(packagesFileName):
    if packagesFileName.endswith('.bz2'):
        file = bz2.BZ2File(packagesFileName, 'r')
    elif packagesFileName.endswith('.gz'):
        file = gzip.open(packagesFileName, 'r')
    else:
        file = open(packagesFileName, 'r')

    localPackages = {}
    package = getPackage(file)
    while package:
        localPackages[package['Package']] = package
        package = getPackage(file)
    file.close()

    return localPackages

def processPackages(url, channel):
    remoteFile, remoteFileName = downloadRemoteFile(url)
    packagesBasePath = os.path.join(RHN_CACHE_ROOT, channel, 'Packages')
    for packagesFileExt in ['', '.gz', '.bz2']:
        packagesFile = packagesBasePath + packagesFileExt
        if os.path.exists(packagesFile) and os.path.isfile(packagesFile):

            localPackages = getLocalPackages(packagesFile)

            tempFile, tempPackagesFile = tempfile.mkstemp()
            tempFile = os.fdopen(tempFile, 'r+b')

            remoteFile.seek(0, 0)
            package = getPackage(remoteFile)
            while package:
                localPackage = localPackages[package['Package']]
                if 'Multi-Arch' in package and package['Multi-Arch'] == 'allowed':
                    localPackage['Multi-Arch'] = 'allowed'
                writePackage(tempFile, localPackage)

                package = getPackage(remoteFile)

            tempFile.close()
            replacePackagesFile(packagesFile, tempPackagesFile)

    remoteFile.close()
    os.remove(remoteFileName)

if __name__ == '__main__':
    parser = setupParser()
    args = parser.parse_args()
    args = vars(args)
    validateArgs(args)
    processPackages(args['url'], args['channel'])
