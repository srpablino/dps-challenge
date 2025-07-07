# DPS Challenge

**Repository:** https://github.com/srpablino/dps-challenge

---

## Overview

DPS is a Document Processing Service. It allows you to upload text files and monitor the resulting text analysis: word count, char count, most common words, text summary etc.
DPS was build with the following tech stack:

- **FastAPI** for HTTP endpoints.
- **SQLite** a lightweight SQL database to store processes status and analysis results.
- A python daemon that monitor new tasks created in the database and process the uploaded files asynchronously.
- Pydantic models to easily construct objects to be persisted on the database and to build responses to requests to the API.
- **Docker support** for easy deployment.
- Structured logging
- The project was developed using **python 3.11**

The project structure:

```
dps-challenge/
├── app/
│   ├── api/                # FastAPI application
│   ├── batch_processing/   # Daemon and processing logic
│   └── shared/             # Shared utilities, DB, logger, config
├── files for testing/      # Directory with 10 text files containing more than 500 words each 
├── tasks/                  # Directory to be created by the system to store files associated to processes
├── postman_collection.json # postman collection to test the API
├── requirements.txt        # project dependencies
├── Dockerfile              # Docker Container Image specification
├── README.md
├── run_docker.bat          # Windows script to build a docker image and run a container
├── run_docker.sh           # Linuex/Mac script to build a docker image and run a container
├── .env                    # Optional env file to define environment variables


```

---
##  Environment variables
You can **optionally** define the following env variables:
- OPEN_AI_KEY: [your open AI API key] : if left out, your results will NOT include the text-summarization part
- TOP_NUMBER_FREQUENT_WORDS: [positive number]: Defines the top N most frequent words found in the processing of the files. If absent, the results will include the full list of words count found during the processing of the files.
- STOP_WORDS: [json list of strings]: defines a list of words that are very common and are preferred to be excluded from the top frequent words found. 

##  Run with Docker
1. Clone the repository  
   ```bash
   git clone https://github.com/srpablino/dps-challenge.git
   cd dps-challenge
   ```
2. Run  
    Run the corresponding .sh or .bat script according your OS.

---
## Run in your host machine without docker
0. (Prerrequisite) Make sure you have python 3.11 installed.

1. Clone the repository  
   ```bash
   git clone https://github.com/srpablino/dps-challenge.git
   cd dps-challenge
   ```

2. Install dependencies  
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Document Processing API script  
   ```bash
   python -m app.api.api_runner
   ```

4. In a sepparated terminal, run the daemon script to process files uploaded through the API:  
   ```bash
   python -m app.batch_processing.daemon
   ```
---


## Swagger / OpenAPI Docs

After launching the project:

- Visit: `http://localhost:8000/docs`  
  This URL opens an interactive Swagger-UI for the API documentation.

---

## Postman Collection

To test the API, you can use the included Postman collection: `dps collection.postman_collection.json`

### To import:

1. Open Postman
2. Click **Import → Choose File**
3. Select `dps collection.postman_collection.json`
4. The collection with defined requests (e.g., file upload endpoint) will appear

---




---