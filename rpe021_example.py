"""
Example RPE-021 REST API implementation based on Python and FastAPI. Note that
JSON schema validation is NOT as tight as in the published schema. Better input
validation is left to competitors, and WILL NOT be tested during the RPE. Only
valid JSON data will be sent to competitor solutions.
"""
from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

elements = {}

class Interface(BaseModel):
    label: str
    interface_id: str
    ipv4: str
    ipv6: str
    mac: str

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
    elem_list = []
    for key, elem in elements.items():
        elem_list.append(elem)
    return {'elements': elem_list}

@app.get('/elements/{id}')
def get_element(id: str):
    element = find_element(id)
    return element

@app.post('/elements')
def add_element(element: Element):
    #print('element: ' + str(element))
    id = element.id
    if id not in elements:
        elements[id] = element
        return element
    else:
        raise HTTPException(status_code=400, detail='Element ID already exists')

@app.put('/elements/{id}')
def update_element(element: Element):
    id = element.id
    origElement = find_element(id)
    elements[id] = element
    return {"orig_element": origElement, "new_element": element}

@app.delete('/elements')
def delete_all_elements():
    elements.clear()
    return {'elements': []}

@app.delete('/elements/{id}')
def delete_element(id: str):
    element = find_element(id)
    del elements[id]
    return element

def find_element(id: str):
    if id in elements:
        return elements[id]
    else:
        raise HTTPException(status_code=404, detail='Element ID not found')
