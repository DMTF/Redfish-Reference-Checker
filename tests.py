# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Reference-Checker/LICENSE.md

import unittest
import RedfishReferenceTool as rst
from bs4 import BeautifulSoup


class TestDMTF(unittest.TestCase):

    def test_get(self):
        uri = "http://redfish.dmtf.org/schemas/v1/Resource_v1.xml"
        success, soup, status = rst.getSchemaFile(uri)

        self.assertEqual(success, True)
        self.assertGreater(len(soup.find_all("edmx:reference")), 0)

    def test_bad_get(self):
        uri = "http://redfish.dmtf.org/index.html"
        success, soup, status = rst.getSchemaFile(uri)
        self.assertEqual(success, False)

    def test_bad_get_2(self):
        uri = "http://baduri"
        success, soup, status = rst.getSchemaFile(uri)
        self.assertEqual(success, False)
    
    def test_bad_alias(self):
        uri = "http://baduri"
        dictin = {uri: 'none'}
        success, soup = rst.getAlias(uri, dictin)
        self.assertEqual(success, False)

    def test_find_refs(self):
        samplexml = '<edmx:Reference Uri="http://docs.oasis-open.org/odata/odata/v4.0/errata03/csd01/complete/vocabularies/Org.OData.Core.V1.xml">\
        <edmx:Include Namespace="Org.OData.Core.V1" Alias="OData"/>\
        </edmx:Reference>\
        <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/RedfishExtensions_v1.xml">\
        <edmx:Include Namespace="RedfishExtensions.v1_0_0" Alias="Redfish"/>\
        </edmx:Reference>\
        <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Resource_v1.xml">\
        <edmx:Include Namespace="Resource"/>\
        <edmx:Include Namespace="Resource.v1_0_0"/>\
        </edmx:Reference>'

        allRefs = ["http://docs.oasis-open.org/odata/odata/v4.0/errata03/csd01/complete/vocabularies/Org.OData.Core.V1.xml",
                   "http://redfish.dmtf.org/schemas/v1/RedfishExtensions_v1.xml", "http://redfish.dmtf.org/schemas/v1/Resource_v1.xml"]

        soup = BeautifulSoup(samplexml, "html.parser")

        self.assertEqual(allRefs, rst.getRefs(soup))


if __name__ == '__main__':
    unittest.main()
