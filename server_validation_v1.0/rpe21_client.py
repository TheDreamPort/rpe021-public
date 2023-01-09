#!/usr/bin/env python3
"""
Client for the RPE-021 REST API.

This script includes trivial REST API validation if invoked directly:
    rpe21_client.py <base_url>

However, this script is primarily intended to be imported as a module by other
Python scripts to provide a high-level wrapper around the REST API. See the
server validation script (validate_server.py) for more thorough REST API
validation.

Copyright 2022-2023, Maryland Innovation and Security Institute
"""

import json
import requests
import sys


class RPE21ClientError(Exception):
    """Generic (unexpected) fatal error"""
    pass


class RPE21Client:
    def __init__(self, baseURL, headers={}):
        """Initializes the client with the base REST API URL and any additional
        headers that must be supplied.
        """
        self.url = baseURL
        self.headers = headers
    
    def clearElements(self):
        """Removes all elements.

        NOTE: For the REST API response, only the status code matters.
        """
        resp = requests.delete(self.url + "/elements", headers=self.headers)
        if resp.status_code != 200:
            raise RPE21ClientError("DELETE /elements returned %d" % (resp.status_code,))

    def getElements(self):
        """Returns a list of all elements."""
        resp = requests.get(self.url + "/elements", headers=self.headers)
        if resp.status_code != 200:
            raise RPE21ClientError("GET /elements returned %d" % (resp.status_code,))
        respJson = resp.json()
        if "elements" not in respJson:
            raise RPE21ClientError("Invalid GET /elements response: %s" % (resp.text,))
        return respJson["elements"]
    
    def addElement(self, element):
        """Adds an element given its JSON definition and returns its endpoint."""
        # Grab the element ID from the provided element definition
        elementId = element["id"]
        resp = requests.post(self.url + "/element", json=element, headers=self.headers)
        if resp.status_code == 400:
            return None  # element ID already exists
        if resp.status_code != 201:
            raise RPE21ClientError("POST /element returned %d" % (resp.status_code,))
        respJson = resp.json()
        if elementId not in respJson:
            raise RPE21ClientError("Invalid POST /element response: %s" % (resp.text,))
        return respJson[elementId]
    
    def uploadElements(self, elements):
        """Bulk upload multiple elements.

        NOTE: For the RPE, only the status code matters since new elements are assumed
        to have the URL /element/<id>. The server validation script will verify the URL,
        but the RPE Data Sender will NOT -- assigning a non-standard URL will impact
        your RPE performance.
        """
        resp = requests.post(self.url + "/elements", json=elements, headers=self.headers)
        if resp.status_code == 403:
            return None  # all uploaded elements failed
        if resp.status_code != 201:
            raise RPE21ClientError("POST /elements returned %d" % (resp.status_code,))
        respJson = resp.json()
        # Removing this check, as any duplicate IDs in the input will yield fewer IDs
        # in the response (list vs. dictionary), and we assume the assigned URLs
        # follow the pattern /element/<id>
#        if len(respJson) != len(elements):
#            raise RPE21ClientError("Invalid POST /elements response: %s" % (resp.text,))
        return respJson
    
    def updateElement(self, element):
        """Updates an existing element given its full, new JSON definition.
        
        NOTE: For the RPE, only the status code matters. The example REST API returns
        the original and new element definitions, but this is NOT required nor used.
        """
        elementId = element["id"]
        resp = requests.put(self.url + "/element/" + elementId, json=element, headers=self.headers)
        if resp.status_code == 404:
            return False  # element ID does not exist
        if resp.status_code != 200:
            raise RPE21ClientError("PUT /element returned %d" % (resp.status_code,))
        return True
    
    def getElement(self, elementId):
        """Retrieves a single element given its ID."""
        resp = requests.get(self.url + "/element/" + elementId, headers=self.headers)
        if resp.status_code == 404:
            return None  # element ID does not exist
        if resp.status_code != 200:
            raise RPE21ClientError("GET /element/%s returned %d" % (elementId, resp.status_code))
        return resp.json()
    
    def deleteElement(self, elementId):
        """Deletes a single element given its ID.
        
        NOTE: For the RPE, only the status code matters. The example REST API returns
        the original element definition, but this is NOT required nor used.
        """
        resp = requests.delete(self.url + "/element/" + elementId, headers=self.headers)
        if resp.status_code == 404:
            return False  # element ID does not exist
        if resp.status_code != 200:
            raise RPE21ClientError("DELETE /element/%s returned %d" % (elementId, resp.status_code))
        return True
    
    def getImage(self):
        """Retrieves the current visualization as an image file.

        NOTE: Since solutions can present either a PNG or a JPG and the REST API does not
        specify which type is "expected", the Content-Type tag must indicate the image type.
        For the RPE, the images will be saved for post-event manual review. This is a required
        feature for the desired capability.
        """
        resp = requests.get(self.url + "/image", headers=self.headers)
        if resp.status_code != 200:
            raise RPE21ClientError("GET /image returned %d" % (resp.status_code,))
        contentType = resp.headers["Content-Type"]
        if contentType not in ["image/png", "image/jpeg"]:
            raise RPE21ClientError("GET /image returned invalid Content-Type '%s'" % (contentType,))
        return contentType, resp.content
    
    def invoke(self, methodStr, endpoint, dataStr=None):
        """Helper function for use with planned simulation data format. Invokes a
        REST API given the method (POST, PUT, GET, or DELETE), the API endpoint,
        and the JSON data in string format.
        """
        # Map the HTTP method to a function pointer
        methodStr = methodStr.upper()
        method = None
        if methodStr == "POST":
            method = requests.post
        elif methodStr == "GET":
            method = requests.get
        elif methodStr == "PUT":
            method = requests.put
        elif methodStr == "DELETE":
            method = requests.delete
        else:
            raise RPE21ClientError('Invalid method "%s"' % (methodStr,))
        
        resp = method(self.url + endpoint, headers=self.headers, data=dataStr)
        return (resp.status_code, resp.json())


def test(args):
    """Performs trivial validation of REST API responses as a means of testing the
    client code above. More thorough server validation is available in a separate
    script.
    """
    if len(args) != 1:
        print('usage: rpe21_client.py <base_url>')
        return 1
    
    client = RPE21Client(args[0])

    print("Clearing elements...")
    client.clearElements()

    print("Verifying no elements...")
    elems = client.getElements()
    if len(elems) != 0:
        print("Expected empty list of elements!")
        return 2

    print("Adding an element...")
    testElem = '{ "id": "dmz_1", "timestamp": "2022-11-10T15:14:00", "label": "DMZ", \
"color": "red", "data": "", "elem_type": "network", "cidr_block": "192.168.200.0/24"}'
    elemUrl = client.addElement(json.loads(testElem))
    if elemUrl != "/element/dmz_1":
        print("Unexpected element URL " + elemUrl)
        return 2
    
    print("Retrieving the new element...")
    print(client.getElement("dmz_1"))

    print("Adding two more elements...")
    testElem2 = '{"id": "wordpress_1", "timestamp": "2022-11-10T15:14:00", \
"label": "WordPress", "color": "red", "data": "", "elem_type": "endpoint", \
"endpoint_type": "server", "os_type": "linux", "network": "dmz_1", "interfaces": \
[{"label": "eth0", "interface_id": "wordpress_1_eth0", "ipv4": "192.168.200.10", \
"mac": "00:01:02:03:04:05"}]}'
    elemUrl = client.addElement(json.loads(testElem2))
    if elemUrl != "/element/wordpress_1":
        print("Unexpected element URL " + elemUrl)
        return 2
    testElem3 = '{"id": "ssh_tunnel_1", "timestamp": "2022-11-10T15:14:00", \
"label": "SSH <Natasha>", "color": "red", "data": "Operator: Natasha", \
"elem_type": "connection", "interface_from": "wordpress_1_eth0", \
"interface_to": "redirector_1_eth0", "line_type": "solid"}'
    elemUrl = client.addElement(json.loads(testElem3))
    if elemUrl != "/element/ssh_tunnel_1":
        print("Unexpected element URL " + elemUrl)
        return 2

    print("Verifying three elements...")
    elems = client.getElements()
    if len(elems) != 3:
        print("Expected list of three elements!")
        return 2
    
    print("Deleting an element...")
    # NOTE: Example returns the deleted element, but this is NOT required for the RPE
    if not client.deleteElement("wordpress_1"):
        print("Failed to delete an existing element!")
        return 2

    print("Verifying two elements...")
    elems = client.getElements()
    if len(elems) != 2:
        print("Expected list of two elements!")
        return 2

    print("Updating an element...")
    updateElem3 = '{"id": "ssh_tunnel_1", "timestamp": "2022-11-10T16:14:00", \
"label": "SSH <Boris>", "color": "red", "data": "Operator: Boris", \
"elem_type": "connection", "interface_from": "wordpress_1_eth0", \
"interface_to": "redirector_1_eth0", "line_type": "solid"}'
    if not client.updateElement(json.loads(updateElem3)):
        print("Failed to update an existing element!")
        return 2
    read3 = client.getElement("ssh_tunnel_1")
    if read3["data"] != "Operator: Boris":
        print("Element update did not take effect!")
        return 2
    
    print("Bulk uploading multiple elements...")
    elements = [json.loads(testElem), json.loads(testElem2), json.loads(testElem3)]
    resp = client.uploadElements(elements)
    if "dmz_1" not in resp or resp["dmz_1"] != "/element/dmz_1":
        print("Failed to update dmz_1!")
    if "wordpress_1" not in resp or resp["wordpress_1"] != "/element/wordpress_1":
        print("Failed to update wordpress_1!")
    if "ssh_tunnel_1" not in resp or resp["ssh_tunnel_1"] != "/element/ssh_tunnel_1":
        print("Failed to update ssh_tunnel_1!")
    # Verify that ssh_tunnel_1 was updated
    readback = client.getElement("ssh_tunnel_1")
    if readback["label"] != "SSH <Natasha>":
        print("Failed to revert ssh_tunnel_1!")
    
    print("Retrieving visualization image file...")
    resp = client.getImage()
    # Example returns the expected JSON, but the 'image' is invalid
    
    print("Verifying 'raw' API...")
    status, resp = client.invoke("DELETE", "/elements")
    if status != 200:
        print("Failed to invoke DELETE /elements!")
    status, resp = client.invoke("POST", "/element", testElem)
    if status != 201 or "dmz_1" not in resp or resp["dmz_1"] != "/element/dmz_1":
        print("Failed to invoke POST /element!")
    status, resp = client.invoke("GET", "/elements", "dmz_1")
    if status != 200 or len(resp) != 1:
        print("Failed to invoke GET /elements!")

    return 0

if __name__ == "__main__":
    sys.exit(test(sys.argv[1:]))
