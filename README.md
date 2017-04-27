Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# Redfish Reference Checker - Version 0.9

## About
RedfishReferenceTool.py is a python3 tool that checks for valid reference URLs in CSDL xml files.
 
## Pre-requisites
* beautifulsoup4  - https://pypi.python.org/pypi/beautifulsoup4/4.1.3
* requests  - https://github.com/kennethreitz/requests (Documentation is available at http://docs.python-requests.org/)

## Installation
Copy RedfishReferenceTool.py into any tool directory, and requires no extra configuration.

Run: python3 RedfishReferenceTool.py [url] [--nocert]

Note that quotations or an escape must be used for '$' and '#' characters, when using ODATA Uris.

## Execution 
Upon execution, attempts to get an XML file at the URL given, and exits with 1
on bad URLs or non xml formatted files, then dereferences all reference URLs
in the file.

Exits with success if the amount of missing references is zero.

