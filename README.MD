# Hello Hauts de seine


## Local dev install 
Required: python <= 3.12 

Run dev  database
```sh
podman compose up -d
```
Create python venv
```sh
python -m venv .venv
```
Activate venv
```sh
source .venv/bin/activate
```

Install dependancies
```sh
pip install -r requirements.txt
```

## Build for staging or production with podman (the same with docker) 

Build image
```sh
  podman build -t pcc:latest . 
  podman run --name pcc-prod -p 80:80 -e POSTGRES_USER=xxxxxx -e POSTGRES_PASSWORD=xxxxxx -e POSTGRES_DB=xxxxxxx -e POSTGRES_HOST=xxxxxx -e POSTGRES_PORT=xxxxx --replace pcc:latest

```

## Test

### run test
Database should be up.
```sh
python -m pytest 
```

