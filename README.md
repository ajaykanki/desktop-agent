# Desktop Agent

## Prerequisites

- OS: Windows
- Python 3.13+
- uv package manager
- Docker Desktop
- SAP Logon 770

## Installation

- Obtain the zscaler-ca certificate from the Trusted Root Certificate Authority (CA) and save it as zscaler-ca.crt in the root directory
- Fill in the .env file and .env.keyring with the necessary configurations
- Run the following commands to start the services:
```sh
uv sync
uv run load_secrets.py # loads .env.keyring into system keyring
docker compose up -d
```
Now you have your windmill stack, task-queue-db, the api service, and the email monitor service under one compose stack

Visit http://localhost to access the windmill instance

See windmill-workspaces repo to configure the windmil instance

## Launching a worker

- A worker needs to be launched to be able to execute tasks
- The worker requires the WORKER, DATABASE, and SAP configurations to be set in the .env file.
- Configure the worker properly to listen to the queues you want to listen to
- Run the following command to start the worker:

```sh
uv run worker.py
```

TODO:
- Compile the worker into a standalone binary
- Run the worker as a background service when the system boots up

## Creating new tasks

TODO

## Notes

- To run only the API service you need to provide the API and Database Configuration in the .env file

- To run the email monitor service you need to provide O365 and WMILL Configuration in the .env file

- To run a standalone worker (windows only) you need to provide the WORKER, Database, and SAP Configuration in the .env file
