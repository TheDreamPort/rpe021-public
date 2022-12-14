"""
Example RPE-021 REST API implementation based on Python and FastAPI. Note that
JSON schema validation is NOT as tight as in the published schema. Better input
validation is left to competitors, and WILL NOT be tested during the RPE. Only
valid JSON data will be sent to competitor solutions.

Copyright 2022, Maryland Innovation and Security Institute
"""

from fastapi import FastAPI, HTTPException, Response
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

elements = {}

# Structure for a network interface
class Interface(BaseModel):
    label: str
    interface_id: str
    ipv4: Optional[str]
    ipv6: Optional[str]
    mac: Optional[str]

# Structure for a network element - network, endpoint, or connection
class Element(BaseModel):
    id: str
    timestamp: datetime
    label: str
    color: str
    data: Optional[str]
    elem_type: str

    # Fields for Network
    cidr_block: Optional[str]

    # Fields for Endpoint
    endpoint_type: Optional[str]
    os_type: Optional[str]
    network: Optional[str]
    interfaces: Optional[List[Interface]]

    # Fields for Connection
    interface_from: Optional[str]
    interface_to: Optional[str]
    line_type: Optional[str]


@app.get('/elements')
def get_all_elements():
    """Return a list of all elements."""
    elem_list = []
    for key, elem in elements.items():
        elem_list.append(elem)
    return {'elements': elem_list}

@app.post('/elements', status_code=201)
def add_element(elem_list: List[Element]):
    """Add or update a list of elements."""
    print('elements: ' + str(elem_list))
    response = {}
    anySuccess = False
    for element in elem_list:
        id = element.id
        # NOTE: Older API version only allowed new elements and rejected
        # changes to existing elements
        elements[id] = element
        response[id] = "/element/" + id
        anySuccess = True
    
    if anySuccess:
        return response
    else:
        raise HTTPException(status_code=403, detail=str(response))

@app.delete('/elements')
def delete_all_elements():
    """Delete all elements."""
    elements.clear()
    # NOTE: Output is not significant, just the HTTP response code (200)
    return {'elements': []}

@app.get('/image', response_class=Response)
def get_image():
    """Return the current visualization as a static image file."""
    # This script just demonstrates the REST API - great visualizations are
    # the job of our participants!
    return Response(content="not-a-png-file", media_type="image/png", status_code=200)

@app.get('/element/{id}')
def get_element(id: str):
    """Return a single element, or 404 if ID is not found."""
    element = find_element(id)
    return element

@app.post('/element', status_code=201)
def add_element(element: Element):
    """Add a single element, or 400 if ID already exists."""
    #print('element: ' + str(element))
    id = element.id
    if id not in elements:
        elements[id] = element
        return {id: "/element/" + id}
    else:
        raise HTTPException(status_code=400, detail='Element ID already exists')

@app.put('/element/{id}')
def update_element(element: Element):
    """Update an existing element, or 404 if ID is not found."""
    id = element.id
    origElement = find_element(id)
    elements[id] = element
    # NOTE: Output is not significant, just the HTTP response code (200/4xx)
    return {"orig_element": origElement, "new_element": element}

@app.delete('/element/{id}')
def delete_element(id: str):
    """Delete an existing element, or 404 if ID is not found."""
    element = find_element(id)
    del elements[id]
    # NOTE: Output is not significant, just the HTTP response code (200/404)
    return element

def find_element(id: str):
    """Helper function to look up an element by ID or throw a HTTP 404 response."""
    if id in elements:
        return elements[id]
    else:
        raise HTTPException(status_code=404, detail='Element ID not found')
