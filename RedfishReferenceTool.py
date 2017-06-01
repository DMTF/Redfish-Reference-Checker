# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Reference-Checker/LICENSE.md

from bs4 import BeautifulSoup
import os
import sys
import requests
import argparse
import json

def getSchemaFile(url, chkCert=False):
    """
    Get a schemafile from a URL, returns None if it fails.

    :param url: given URL
    :returns a Soup object
    """

    soup = None
    filedata = None
    success = False
    status = ''
    # rs-assertion: no authorization expected for schemagrabbing
    try:
        r = requests.get(url,verify=chkCert)
        filedata = r.text
        status = r.status_code
        doctype = r.headers.get('content-type')
        # check if file is returned and is legit XML
        if "xml" in doctype and status in [200, 204] and filedata:
            soup = BeautifulSoup(filedata, "html.parser")
            success = True
    except Exception as ex:
        print("Something went wrong: %s %s" % (ex, status), file=sys.stderr)

    return success, soup, status


def getRefs(soup):
    """
    Get reference URLs from a legitimate schema.

    param: soup: bs4 soup object
    return: list of refs
    """
    references = soup.find_all('edmx:reference')
    refurls = [ref.get('uri') for ref in references]
    return refurls

def getAlias(uri, aliasDict):
    """
    Grab a file from an alias from an alias dictionary

    param uri: uri
    param aliasDict: references to a local file for a uri
    return boolean, soup
    """
    soup = None
    if uri in aliasDict:
        fileName = aliasDict[uri]
        if not os.path.isfile(fileName):
            print("No such file: %s %s" % (uri, fileName), file=sys.stderr) 
            return False, None
        with open(fileName) as f:
            print(fileName)
            fileData = f.read()
            soup = BeautifulSoup(fileData, "html.parser")
            print("Using alias: {} {}".format(uri, fileName))
    return soup is not None, soup

if __name__ == "__main__":
    chkCert = True

    argget = argparse.ArgumentParser(description='Tool that checks if reference contain all valid URLs')
    argget.add_argument('url', type=str, help='url to test')
    argget.add_argument('--nochkcert', action='store_true', help='ignore check for certificate')
    argget.add_argument('--alias', type=str, default=None, help='location of alias json file')
    
    args = argget.parse_args()

    rootURL = args.url
    chkCert = not args.nochkcert
    aliasFile = args.alias
    
    aliasDict = dict()
    if aliasFile is not None:
        print("Using alias file: " + aliasFile)
        with open(aliasFile) as f:
            aliasDict.update( json.loads(f.read()) )
            print (aliasDict)

    rootHost = rootURL.rsplit('/',rootURL.count('/')-2)[0]
    print(rootHost)
    print(rootURL)
    success, rootSoup = getAlias(rootURL, aliasDict)
    if not success:
        success, rootSoup, status = getSchemaFile(rootURL, chkCert)

    if not success:
        print("No Schema Found at URL")
        sys.exit(1)

    missingRefs = 0
    refs = getRefs(rootSoup)
    allRefs = set()

    # loop that finds all URLs and checks for missing or malformed items
    while len(refs) > 0:
        newRefs = []
        for ref in refs:
            if ref in allRefs:
                continue
            allRefs.add(ref)
            print(ref)

            success, soupOfRef = getAlias(ref, aliasDict)
            if not success:
                success, soupOfRef, status = getSchemaFile(ref if 'http' in ref[:8] else rootHost+ref, chkCert = chkCert)
            if success:
                newRefs += getRefs(soupOfRef)
            else:
                print (success, soupOfRef, status)
                missingRefs += 1
                print ("Something went wrong in script: No Valid Schema Found", missingRefs, file=sys.stderr)
        refs = newRefs

    if len(allRefs) > 0:
        print("Work complete, total failures: ", missingRefs)
        print("Total references: ", len(allRefs))
    else:
        print("No references found.")

    if missingRefs > 0:
        sys.exit(1)

    sys.exit(0)
