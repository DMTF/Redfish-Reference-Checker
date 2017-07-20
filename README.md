Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# Redfish Reference Checker - Version 0.9

## About
RedfishReferenceTool.py is a python3 tool that checks for valid reference URLs in CSDL xml files.
 
## Pre-requisites
The following requirements may be installed via the command line:

pip3 install -r requirements.txt

The requirements for this tool are as follows:

* beautifulsoup4  - https://pypi.python.org/pypi/beautifulsoup4/4.5.3 
* requests  - https://github.com/kennethreitz/requests (Documentation is available at http://docs.python-requests.org/)

Warning: BeautifulSoup4 is required to be <=4.5.3, and will not attempt to run without the appropriate version

## Installation
Copy RedfishReferenceTool.py into any tool directory, and requires no extra configuration.

Run: python3 RedfishReferenceTool.py [url] [--nocert] [--alias file]

URL includes authority.  Note that quotations or an escape must be used for '$' and '#' characters, when using ODATA Uris.

## Execution 
Upon execution, attempts to get an XML file at the URL given, and exits with 1
on bad URLs or non xml formatted files, then dereferences all reference URLs
in the file.

Upon specifying --nocert, it will not attempt to verify any certification provided.

Upon specifying --alias, it will read a json-formatted file that provides an alias for URIs or URLs not currently published online,
and instead points to a local file.

Exits with success if the amount of missing references is zero.

