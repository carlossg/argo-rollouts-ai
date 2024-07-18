# Argo Rollouts Analysis using AI

Example Argo Rollouts Analysis that uses AI services to provide a better explanation
of what has happened during rollout.

# Setup

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export GOOGLE_API_KEY=...
```

## Adding dependencies

```
pip install langchain-google-genai
python3 -m pip freeze > requirements.txt
```

# Langchain

[tutorial](https://python.langchain.com/v0.2/docs/tutorials/llm_chain/)

# Running

```
python app.py https://example.com
```

# Running in Docker

```
make build
docker run -ti --rm \
    -e GOOGLE_API_KEY \
    csanchez/argo-rollouts-ai
```

# Building docker images

```shell
make build
```
