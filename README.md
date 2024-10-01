# Argo Rollouts Analysis using AI

Example Argo Rollouts Analysis that uses AI services to do the canary analysis.

This job can be executed as a Argo Rollouts canary analysis job.
It will fetch the logs from pods with the label `role=stable` and `role=canary`
and use an AI model to compare both logs to decide whether the canary promotion
should continue or not.

The result is returned from the model as a json file like:

```json
{
    "text": "Canary deployment encountered Bad Request errors (HTTP 400) due to image pulling failures, indicating a problem with the canary version's image or configuration.  The stable version did not exhibit these errors.",
    "promote": false,
    "confidence": 95
}
```

Tested with:

* Google Gemini

# Usage

Argo Rollouts allows different sources for analysis, one of them being the execution of a job.

In your `Rollout` object set the `spec.metrics.provider.job` to something like the following.
[Full example](examples/analysis-success-rate-job-ai.yaml).

```yaml
        metadata:
          annotations:
            service: "{{args.service}}"
          labels:
            service: "{{args.service}}"
        spec:
          backoffLimit: 0
          ttlSecondsAfterFinished: 1200
          template:
            metadata:
              labels:
                app: success-rate-job-ai
            spec:
              restartPolicy: Never
              containers:
              - name: ai
                image: us-central1-docker.pkg.dev/api-project-642841493686/github/argo-rollouts-ai:580503203f0460f299e1f4de569b5876c597a37b
                imagePullPolicy: IfNotPresent
                env:
                - name: GOOGLE_API_KEY
                  valueFrom:
                    secretKeyRef:
                      name: success-rate-job-ai
                      key: google_api_key
                volumeMounts:
                - name: empty
                  mountPath: /logs
                # - name: code
                #   mountPath: /app
                resources:
                  requests:
                    memory: "32Mi"
                    cpu: "250m"
                  limits:
                    memory: "64Mi"
                    cpu: "500m"
              volumes:
              - name: empty
                emptyDir: {}
              # - name: code
              #   configMap:
              #     name: canary-demo-6mm6k4ffck
```

# Development Setup

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

# Notes

Google Cloud credits are provided for this project.

#AISprint
