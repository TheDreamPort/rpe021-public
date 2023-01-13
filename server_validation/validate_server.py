#!/usr/bin/env python3
"""
Script that validates an RPE-021 REST API to ensure that all APIs behave as
designed. Competitors should use this prior to the competition to verify operation
of their capability AND to identify any integration issues prior to the event.

For competitors with special headers (e.g., API key), the spot to change in the
code is identified below.

Copyright 2022-2023, Maryland Innovation and Security Institute
"""

import json
import rpe21_client
import sys
import unittest

# This gets filled in from the command line
BASE_URL = None

# Add your headers here if necessary
HEADERS = {}


class TestRestApi(unittest.TestCase):
    # Test elements (string form)
    DMZ_1 = '{ "id": "dmz_1", "timestamp": "2022-11-10T15:14:00", "label": "DMZ", \
"color": "red", "data": "", "elem_type": "network", "cidr_block": "192.168.200.0/24"}'
    WORDPRESS_1 = '{"id": "wordpress_1", "timestamp": "2022-11-10T15:14:00", \
"label": "WordPress", "color": "red", "data": "", "elem_type": "endpoint", \
"endpoint_type": "server", "os_type": "linux", "network": "dmz_1", "interfaces": \
[{"label": "eth0", "interface_id": "wordpress_1_eth0", "ipv4": "192.168.200.10", \
"mac": "00:01:02:03:04:05"}]}'
    SSH_TUNNEL_1 = '{"id": "ssh_tunnel_1", "timestamp": "2022-11-10T15:14:00", \
"label": "SSH <Natasha>", "color": "red", "data": "Operator: Natasha", \
"elem_type": "connection", "interface_from": "wordpress_1_eth0", \
"interface_to": "redirector_1_eth0", "line_type": "solid"}'

    def setUp(self):
        # NOTE: Add your custom headers here as the second parameter
        self.client = rpe21_client.RPE21Client(BASE_URL, HEADERS)
        # Ensure each test case starts with a clean slate. If this API doesn't
        # work, nearly all tests will fail
        self.client.clearElements()

    def tearDown(self):
        pass

    def test_get_all_elements_empty(self):
        elements = self.client.getElements()
        self.assertEqual(len(elements), 0)

    def test_add_element(self):
        url = self.client.addElement(json.loads(self.DMZ_1))
        self.assertEqual(url, "/element/dmz_1")
        elements = self.client.getElements()
        self.assertEqual(len(elements), 1)

    def test_add_duplicate_elem(self):
        url = self.client.addElement(json.loads(self.DMZ_1))
        self.assertEqual(url, "/element/dmz_1")
        url = self.client.addElement(json.loads(self.DMZ_1))
        self.assertIsNone(url)
        elements = self.client.getElements()
        self.assertEqual(len(elements), 1)

    def test_add_duplicate_id(self):
        url = self.client.addElement(json.loads(self.DMZ_1))
        self.assertEqual(url, "/element/dmz_1")
        elem2 = json.loads(self.WORDPRESS_1)
        elem2["id"] = "dmz_1" # duplicate ID, different type of element
        url = self.client.addElement(elem2)
        self.assertIsNone(url)
        elements = self.client.getElements()
        self.assertEqual(len(elements), 1)

    @unittest.expectedFailure
    def test_add_invalid_type(self):
        # NOTE: The "expectedFailure" is due to limitations in my example REST API
        # in rpe021_example.py. A more robust implementation would perform better
        # input validation. If your implementation validates "elem_type", remove the
        # expectedFailure decorator above. There could obviously be a much larger
        # suite of tests for input validation, but since I didn't have time to
        # implement the validation, I also didn't have time to implement the tests.
        elem = json.loads(self.DMZ_1)
        elem["elem_type"] = "not_valid"
        url = self.client.addElement(elem)
        self.assertIsNone(url, "example REST API does little input validation")
        elements = self.client.getElements()
        self.assertEqual(len(elements), 0)

    def test_delete_element(self):
        url = self.client.addElement(json.loads(self.DMZ_1))
        self.assertEqual(url, "/element/dmz_1")
        self.assertEqual(self.client.deleteElement("dmz_1"), True)
        elements = self.client.getElements()
        self.assertEqual(len(elements), 0)

    def test_delete_missing(self):
        url = self.client.addElement(json.loads(self.DMZ_1))
        self.assertEqual(url, "/element/dmz_1")
        self.assertEqual(self.client.deleteElement("wordpress_1"), False)
        elements = self.client.getElements()
        self.assertEqual(len(elements), 1)

    def test_delete_double(self):
        url = self.client.addElement(json.loads(self.DMZ_1))
        self.assertEqual(url, "/element/dmz_1")
        self.assertEqual(self.client.deleteElement("dmz_1"), True)
        self.assertEqual(self.client.deleteElement("dmz_1"), False)
        elements = self.client.getElements()
        self.assertEqual(len(elements), 0)

    def test_update_element(self):
        dmz1 = json.loads(self.DMZ_1)
        url = self.client.addElement(dmz1)
        self.assertEqual(url, "/element/dmz_1")
        dmz1["color"] = "orange"
        dmz1["timestamp"] = "2022-11-11T12:34:56"
        self.assertEqual(self.client.updateElement(dmz1), True)
        elements = self.client.getElements()
        self.assertEqual(len(elements), 1)

    def test_update_deleted(self):
        dmz1 = json.loads(self.DMZ_1)
        url = self.client.addElement(dmz1)
        self.assertEqual(url, "/element/dmz_1")
        self.assertEqual(self.client.deleteElement("dmz_1"), True)
        dmz1["color"] = "orange"
        dmz1["timestamp"] = "2022-11-11T12:34:56"
        self.assertEqual(self.client.updateElement(dmz1), False)
        elements = self.client.getElements()
        self.assertEqual(len(elements), 0)

    def test_update_missing(self):
        dmz1 = json.loads(self.DMZ_1)
        url = self.client.addElement(dmz1)
        self.assertEqual(url, "/element/dmz_1")
        self.assertEqual(self.client.updateElement(json.loads(self.WORDPRESS_1)), False)
        elements = self.client.getElements()
        self.assertEqual(len(elements), 1)

    def test_get_element(self):
        url = self.client.addElement(json.loads(self.DMZ_1))
        self.assertEqual(url, "/element/dmz_1")
        elem = self.client.getElement("dmz_1")
        self.assertEqual(elem["id"], "dmz_1")
        self.assertEqual(elem["timestamp"], "2022-11-10T15:14:00")
        self.assertEqual(elem["label"], "DMZ")
        self.assertEqual(elem["color"], "red")
        self.assertEqual(elem["data"], "")
        self.assertEqual(elem["elem_type"], "network")
        self.assertEqual(elem["cidr_block"], "192.168.200.0/24")

    def test_get_missing(self):
        url = self.client.addElement(json.loads(self.DMZ_1))
        self.assertEqual(url, "/element/dmz_1")
        elem = self.client.getElement("dmz_2")
        self.assertIsNone(elem)

    def test_get_deleted(self):
        url = self.client.addElement(json.loads(self.DMZ_1))
        self.assertEqual(url, "/element/dmz_1")
        self.assertEqual(self.client.deleteElement("dmz_1"), True)
        elem = self.client.getElement("dmz_1")
        self.assertIsNone(elem)
    
    def test_slow_bulk_add(self):
        wordpress = json.loads(self.WORDPRESS_1)
        for i in range(100):
            newId = "wordpress_%d" % (i,)
            wordpress["id"] = newId
            url = self.client.addElement(wordpress)
            self.assertEqual(url, "/element/" + newId)
        elements = self.client.getElements()
        self.assertEqual(len(elements), 100)
    
    def test_upload_elements(self):
        elements = []
        for i in range(100):
            newId = "wordpress_%d" % (i,)
            wordpress = json.loads(self.WORDPRESS_1)
            wordpress["id"] = newId
            wordpress["interfaces"][0]["interface_id"] = "wordpress_%d_eth0" % (i,)
            elements.append(wordpress)
        resp = self.client.uploadElements(elements)
        for id in resp:
            self.assertTrue(id.startswith("wordpress_"))
            self.assertEqual(resp[id], "/element/" + id)
        elements = self.client.getElements()
        self.assertEqual(len(elements), 100)
    
    def test_upload_duplicate(self):
        # NOTE: API was changed on 12/22/2022 to allow bulk upload of changes as well
        # as new elements. Therefore, a single update can also specify the same ID
        # multiple times -- the last update in the list "sticks". This unit test was
        # changed accordingly.
        wordpress = json.loads(self.WORDPRESS_1)
        wordpress2 = json.loads(self.WORDPRESS_1)
        wordpress2["os_type"] = "windows"
        elements = [wordpress, wordpress2]
        resp = self.client.uploadElements(elements)
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp["wordpress_1"], "/element/wordpress_1")
        elements = self.client.getElements()
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0]["os_type"], "windows")
    
    def test_upload_update(self):
        elements = [json.loads(self.DMZ_1), json.loads(self.WORDPRESS_1)]
        resp = self.client.uploadElements(elements)
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp["dmz_1"], "/element/dmz_1")
        self.assertEqual(resp["wordpress_1"], "/element/wordpress_1")
        # This would be a realistic use of bulk updates as node status changes
        # during a pentest
        elements[0]["color"] = "orange"
        elements[1]["color"] = "orange"
        resp = self.client.uploadElements(elements)
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp["dmz_1"], "/element/dmz_1")
        self.assertEqual(resp["wordpress_1"], "/element/wordpress_1")
        # Elements were altered
        elements = self.client.getElements()
        self.assertEqual(len(elements), 2)
        elem = self._findElement(elements, "dmz_1")
        self.assertIsNotNone(elem)
        self.assertEqual(elem["color"], "orange")
        elem = self._findElement(elements, "wordpress_1")
        self.assertIsNotNone(elem)
        self.assertEqual(elem["color"], "orange")
    
    def test_upload_partial_success(self):
        elements = [json.loads(self.DMZ_1), json.loads(self.WORDPRESS_1)]
        resp = self.client.uploadElements(elements)
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp["dmz_1"], "/element/dmz_1")
        self.assertEqual(resp["wordpress_1"], "/element/wordpress_1")
        # This would be a realistic use of bulk updates as node status changes
        # during a pentest
        elements[0]["color"] = "orange"
        elements[1] = json.loads(self.SSH_TUNNEL_1)
        resp = self.client.uploadElements(elements)
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp["dmz_1"], "/element/dmz_1")
        self.assertEqual(resp["ssh_tunnel_1"], "/element/ssh_tunnel_1")
        # Element was altered
        elements = self.client.getElements()
        self.assertEqual(len(elements), 3)
        elem = self._findElement(elements, "dmz_1")
        self.assertIsNotNone(elem)
        self.assertEqual(elem["color"], "orange")
        elem = self._findElement(elements, "wordpress_1")
        self.assertIsNotNone(elem)
        self.assertEqual(elem["color"], "red")
        elem = self._findElement(elements, "ssh_tunnel_1")
        self.assertIsNotNone(elem)
    
    def test_get_image(self):
        elements = []
        for i in range(20):
            newId = "wordpress_%d" % (i,)
            wordpress = json.loads(self.WORDPRESS_1)
            wordpress["id"] = newId
            wordpress["interfaces"][0]["interface_id"] = "wordpress_%d_eth0" % (i,)
            elements.append(wordpress)
        resp = self.client.uploadElements(elements)
        self.assertEqual(len(resp), 20)
        # Very little validation - the RPE21Client class validates Content-Type
        image = self.client.getImage()
        self.assertIsNotNone(image)

    def _findElement(self, elem_list, id):
        for elem in elem_list:
            if elem["id"] == id:
                return elem
        return None


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: validate_server.py <url>')
    else:
        BASE_URL = sys.argv[1]
        sys.argv.pop(1)
        unittest.main()
