"""
Example RPE-021 REST API implementation based on Python and FastAPI. Note that
JSON schema validation is NOT as tight as in the published schema. Better input
validation is left to competitors, and WILL NOT be tested during the RPE. Only
valid JSON data will be sent to competitor solutions.

Copyright 2022, Maryland Innovation and Security Institute
"""

from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

elements = {}

# Structure for a network interface
class Interface(BaseModel):
    label: str
    interface_id: str
    ipv4: str
    ipv6: str
    mac: str

# Structure for a network element - network, endpoint, or connection
class Element(BaseModel):
    id: str
    timestamp: datetime
    label: str
    color: str
    data: str
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

@app.get('/elements/{id}')
def get_element(id: str):
    """Return a single element, or 404 if ID is not found."""
    element = find_element(id)
    return element

@app.post('/elements')
def add_element(element: Element):
    """Add a single element, or 400 if ID already exists."""
    #print('element: ' + str(element))
    id = element.id
    if id not in elements:
        elements[id] = element
        # NOTE: Output is not significant, just the HTTP response code (200/4xx)
        return element
    else:
        raise HTTPException(status_code=400, detail='Element ID already exists')

@app.put('/elements/{id}')
def update_element(element: Element):
    """Update an existing element, or 404 if ID is not found."""
    id = element.id
    origElement = find_element(id)
    elements[id] = element
    # NOTE: Output is not significant, just the HTTP response code (200/4xx)
    return {"orig_element": origElement, "new_element": element}

@app.delete('/elements')
def delete_all_elements():
    """Delete all elements."""
    elements.clear()
    # NOTE: Output is not significant, just the HTTP response code (200)
    return {'elements': []}

@app.delete('/elements/{id}')
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
