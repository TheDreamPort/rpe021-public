# DreamPort RPE-021 Public Files

Welcome to [DreamPort RPE-021](https://dreamport.tech/events/event-rpe-021-visualizing-the-future.php), "Visualizing the Future", a penetration testing visualization challenge!

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

Alternatively, a simple [Dockerfile](/Dockerfile) is provided to build and run as a Docker container:

        docker build . -t rpe021-example
        docker run -d rpe021-example

The REST API can then be invoked as desired:

        curl http://127.0.0.1:8000/elements
        curl -X POST -H "Content-type: application/json" -d @ex_full1.json http://172.17.0.2/elements

### Server Validation and REST Client

Repo link: [validate_server.py](/server_validation_v1.0/validate_server.py)
Repo link: [rpe21_client.py](/server_validation_v1.0/rpe21_client.py)

The REST API server validation script uses the Python `unittest` framework to validate compatibility of a specified REST API implementation with expectations for RPE-021. The only non-standard dependency is `requests`, which is identified in the [requirements.txt](/server_validation_v1.0/requirements.txt) file and is easily installed via `pip`.

To run the script on Linux:

        python3 -m venv venv
        source ven/bin/activate
        pip install -r requirements.txt
        ./validate_server.py http://competitor.com/rpe21_base

If necessary, edit `validate_server.py` where indicated to add any custom headers, e.g., `X-API-Key` for a required API key.

**IMPORTANT**: If you believe any changes need to be made to `rpe021_client.py` for compatibility with your REST API, please [contact us](mailto:rpe-submission@dreamport.tech) ASAP! We are NOT planning to accommodate custom REST client scripts -- we plan to use `rpe21_client.py` as is for all competitors, supplying only the base URL and a map of any custom HTTP headers.

## Questions?

Please contact [rpe-submission@dreamport.tech](mailto:rpe-submission@dreamport.tech) with any questions.
