build:
	docker buildx build --platform linux/amd64,linux/arm64 \
		-t csanchez/argo-rollouts-ai .

push:
	docker buildx build --push --platform linux/amd64,linux/arm64 \
		--cache-to type=registry,ref=csanchez/argo-rollouts-ai:buildcache,mode=max \
		--cache-from type=registry,ref=csanchez/argo-rollouts-ai:buildcache,mode=max \
		-t csanchez/argo-rollouts-ai .

run:
	python3 app.py
