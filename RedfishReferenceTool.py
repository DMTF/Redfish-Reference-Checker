# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Reference-Checker/LICENSE.md

from bs4 import BeautifulSoup
import os
import sys
import requests


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
        sys.stderr.write("Something went wrong: %s %s" % (ex, status))

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


if __name__ == "__main__":
    rootURL = None
    chkCert = True

    for arg in sys.argv[1:]:
        if arg == '--nocert' and chkCert == True:
            chkCert = False
        elif rootURL is None:
            rootURL = arg
        else:
            print("invalid option:", arg)
            sys.exit(1)
    if len(sys.argv) > 3 or rootURL is None:
        print("usage: RedfishReferenceTool.py [url] [--nocert]")
        sys.exit(1)
    rootHost = rootURL.rsplit('/',rootURL.count('/')-2)[0]
    print(rootHost)
    print(rootURL)
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
            success, soupOfRef, status = getSchemaFile(ref if 'http' in ref[:8] else rootHost+ref, chkCert = chkCert)
            if success:
                newRefs += getRefs(soupOfRef)
            else:
                print (success, soupOfRef, status)
                missingRefs += 1
                print (
                    "Something went wrong in script: No Valid Schema Found", missingRefs)
        refs = newRefs

    if len(allRefs) > 0:
        print("Work complete, total failures: ", missingRefs)
        print("Total references: ", len(allRefs))
    else:
        print("No references found.")

    if missingRefs > 0:
        sys.exit(1)

    sys.exit(0)
