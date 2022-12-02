# DreamPort RPE-021 Public Files

Welcome to DreamPort RPE-021, a penetration testing visualization challenge!

## Provided Files

We are happy to provide the following files in support of the RPE.

### JSON Schema

Repo link: [rpe021_schema.json](/rpe021_schema.json)

The JSON Schema definition for the REST API that participants must implement. Refer to [Understanding JSON Schema](https://json-schema.org/understanding-json-schema/index.html) for the language definition. We also found this [Online JSON Schema Validator](https://www.jsonschemavalidator.net/) very helpful.

> NOTE: DreamPort has no affiliation with either of these sites. This isn't an endorsement, YMMV.

### Example REST API Implementation

Repo link: [rpe021_example.py](/rpe021_example.py)

This simple Python script leverages the FastAPI framework to demonstrate the REST API to be implemented in this RPE. The script was tested on Python 3.10.6 and fastapi 0.86.0, and is provided with no warranty. ;-)

The script was developed to validate the REST API and JSON schema. It is being shared to demonstrate a working example **and** annotations indicating which parts of the API (e.g., outputs from each API endpoint) are important to the competition.

To run the script on Linux:

        python3 -m venv venv
        source venv/bin/activate
        pip install wheel fastapi[all]
        uvicorn rpe021_example:app

The REST API can then be invoked, e.g., `curl http://127.0.0.1:8000/elements`.

## Questions?

Please contact [rpe-submission@dreamport.tech](mailto:rpe-submission@dreamport.tech) with any questions.
