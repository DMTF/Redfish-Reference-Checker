# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Reference-Checker/LICENSE.md

from glob import glob
from bs4 import BeautifulSoup
import os
import sys
import requests
import argparse
import json
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def generateXmlReferences(reftags):
    # unused block to write a valid xml file instead of just printing to file
    xml_node = Element('edmx:Edmx')
    xml_node.set('Version', '4.0')
    xml_node.set('xmlns:edmx', 'http://docs.oasis-open.org/odata/ns/edmx')

    output_string = ""
    for tag in reftags:
        output_string += str(tag) + '\n'
    return output_string


def checkInvalidTags(soup):
    expected_tags = ['Edmx', 'Reference', 'Include', 'DataServices', 'Schema', 'EntityContainer']
    bad_tags = list()
    for tag in soup.find_all(True):
        if tag.name not in bad_tags:
            if tag.name not in expected_tags and tag.name.lower() in [x.lower() for x in expected_tags]:
                bad_tags.append(tag.name)
    if len(bad_tags) > 0:
        print('The following tags were found that may be misspelled or the wrong case:')
        for tag in bad_tags:
            print('    ' + tag)


def getSchemaFile(url, chkCert=False, to=30):
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
        r = requests.get(url, verify=chkCert, timeout=to)
        filedata = r.text
        status = r.status_code
        doctype = r.headers.get('content-type')
        # check if file is returned and is legit XML
        if "xml" in doctype and status in [200, 204] and filedata:
            soup = BeautifulSoup(filedata, "xml")
            checkInvalidTags(soup)
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
    reftags = soup.find_all('edmx:Reference')
    refs = [(ref.get('Uri'), ref) for ref in reftags]
    for cnt, url in enumerate(refs):
        if url is None:
            print("The Uri in this Reference #{} is missing, please check for capitalization of Uri".format(cnt))
    return refs


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
            soup = BeautifulSoup(fileData, "xml")
            checkInvalidTags(soup)
            print("Using alias: {} {}".format(uri, fileName))
    return soup is not None, soup


if __name__ == "__main__":
    argget = argparse.ArgumentParser(description='Tool that checks if reference contain all valid URLs')
    argget.add_argument('url', type=str, help='destination url to test')
    argget.add_argument('--file', action='store_true', help='use url as filepath to local file')
    argget.add_argument('--nochkcert', action='store_true', help='ignore check for certificate')
    argget.add_argument('--alias', type=str, default=None, help='location of alias json file')
    argget.add_argument('--timeout', type=int, default=30, help='timeout for requests')
    argget.add_argument('--refoutput', type=str, help='Output file for all refs found in files')

    args = argget.parse_args()

    rootURL = args.url
    chkCert = not args.nochkcert
    aliasFile = args.alias

    aliasDict = dict()

    if args.refoutput is not None and os.path.isfile(args.refoutput):
        print("File exists for {}, aborting".format(args.refoutput), file=sys.stderr)
        sys.exit(10)

    if aliasFile is not None:
        print("Using alias file: " + aliasFile)
        with open(aliasFile) as f:
            filedict = json.loads(f.read())
            # if entry ends in asterisk, replace it with ever file in asterisk directory on right
            for key in filedict:
                if '*' in key:
                    filelist = glob(filedict[key])
                    for f in filelist:
                        path, name = os.path.split(f)
                        aliasKey = key.replace('*', name)
                        aliasDict[aliasKey] = f
                else:
                    aliasDict[key] = filedict[key]
            for key in aliasDict:
                print(key, aliasDict[key])

    if not args.file:
        rootHost = rootURL.rsplit('/', rootURL.count('/') - 1)[0]
        print(rootHost)
        print(rootURL)
        success, rootSoup = getAlias(rootURL, aliasDict)
        if not success:
            success, rootSoup, status = getSchemaFile(rootURL, chkCert, args.timeout)

    else:
        # Let's make a bogus alias dict and use it
        rootHost = None
        success, rootSoup = getAlias("local", {"local": rootURL})
        if not success:
            sys.exit(1)

    if not success:
        print("No Schema Found for given destination, is this a proper xml? {}".format(rootURL))
        sys.exit(1)

    missingRefs = list()
    refs = getRefs(rootSoup)
    allRefs = set()
    allTags = set()

    # loop that finds all URLs and checks for missing or malformed items
    while len(refs) > 0:
        newRefs = []
        for ref, tag in refs:
            if ref in allRefs:
                continue
            if ref not in allRefs:
                allRefs.add(ref)
                allTags.add(tag)
            print(ref)

            success, soupOfRef = getAlias(ref, aliasDict)
            if not success:
                if 'http' in ref[:8]:
                    success, soupOfRef, status = getSchemaFile(ref, chkCert, args.timeout)
                elif rootHost is not None:
                    success, soupOfRef, status = getSchemaFile(rootHost+ref, chkCert, args.timeout)
                else:
                    print("in file mode, yet contains local uri")
            if success:
                newRefs += getRefs(soupOfRef)
            else:
                print(success, soupOfRef, status)
                missingRefs += ref
                print("Something is wrong: No Valid Schema Found #{}".format(len(missingRefs)), file=sys.stderr)
        refs = newRefs

    if args.refoutput is not None:
        with open(args.refoutput, 'w', encoding='utf-8') as reffile:
            for item in allTags:
                reffile.write(str(item.prettify()))

    if len(allRefs) > 0:
        print("Work complete, total failures: ", len(missingRefs))
        for miss in missingRefs:
            print(str(miss))
        print("Total references: ", len(allRefs))
    else:
        print("No references found, if this is incorrect, check capitalization/spelling of xml tags.")

    if len(missingRefs) > 0:
        sys.exit(1)

    sys.exit(0)
