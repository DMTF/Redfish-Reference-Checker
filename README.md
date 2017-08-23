Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# Redfish Reference Checker - Version 0.9

## About
RedfishReferenceTool.py is a python3 tool that checks for valid reference URLs in CSDL xml files.
 
## Pre-requisites
The following requirements may be installed via the command line:

pip3 install -r requirements.txt

The requirements for this tool are as follows:

* beautifulsoup4  - https://pypi.python.org/pypi/beautifulsoup4
* requests  - https://github.com/kennethreitz/requests (Documentation is available at http://docs.python-requests.org/)
* lxml - https://pypi.python.org/pypi/lxml

## Installation
Copy RedfishReferenceTool.py into any tool directory, and requires no extra configuration.

Run: python3 RedfishReferenceTool.py [url] [--nochkcert] [--alias file] [--file] [--timeout]

URL includes authority.  Note that quotations or an escape must be used for '$' and '#' characters, when using ODATA Uris.

## Execution 
Upon execution, attempts to get an XML file at the URL given, and exits with 1
on bad URLs or non xml formatted files, then dereferences all reference URLs
in the file.

Upon specifying --nochkcert, it will not attempt to verify any certification provided.  --timeout may be used to increase request timeouts.

Upon specifying --alias, it will read a json-formatted file that provides an alias for URIs or URLs not currently published online,
and instead points to a local file.  
For single files, a single URL may be mapped on the left hand side to point to a file stored on the right.  
If a URL is appended with /\*, then it may point to a directory appended with /\* on the right, such that each file in the directory will be mapped to its own URL.

For a simpler way to test one local file, please use the parameter --file, which will interpret the URL given as a locally stored file relative to the current work directory.  This mode will not interpret a "host", and thus will fail if the stored file contains relative references.

Exits with success if the amount of missing references is zero.

