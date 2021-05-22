# Server



## Run

```bash

pipenv shell

# initial database
python scripts/initial_database.py
python scripts/initial_data.py
python scripts/initial_services.py
uvicorn app.main:app --reload

```

## Generate Requirement

```bash

pipenv lock -r > requirements.txt

```

```bash

docker run -d -v /var/run/docker.sock:/var/run/docker.sock mblocks/server

```
