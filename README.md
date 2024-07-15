# Argo Rollouts Analysis using AI

Example Argo Rollouts Analysis that uses AI services to provide a better explanation
of what has happened during rollout.

# Setup

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export AZURE_OPENAI_API_KEY=...
```

## Adding dependencies

```
pip install langchain-openai
python3 -m pip freeze > requirements.txt
```

# Langchain

[tutorial](https://python.langchain.com/v0.2/docs/tutorials/llm_chain/)

# Running

```
python app.py
```

# Running in Docker

```
docker build -t csanchez/argo-rollouts-ai .
docker run -ti --rm \
    -e AZURE_OPENAI_API_KEY \
    csanchez/argo-rollouts-ai
```
