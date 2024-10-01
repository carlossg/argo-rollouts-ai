import time
import os
import requests
import sys

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.callbacks import get_openai_callback
from dotenv import load_dotenv

from kubernetes import client, config

# read .env variables
load_dotenv()

# if /logs exists use it, otherwise use app.log
log_dir = "/logs" if os.path.exists("/logs") else "./logs"
log_stable_file_name = os.path.join(log_dir, "app-stable.log")
log_canary_file_name = os.path.join(log_dir, "app-canary.log")

# first argument is service url
url = sys.argv[1] if len(sys.argv) > 1 else None
# if not url:
#     print("Please provide the url as an argument.")
#     sys.exit(1)

# initial sleep
sleep = 0
print(f"Sleeping for {sleep} seconds")
time.sleep(sleep)

return_code = 0

# Configure the Kubernetes client
config.load_kube_config()

# Create an API client
v1 = client.CoreV1Api()


# Get the current namespace from the kubeconfig file or from inside the pod
def get_current_namespace(context: str = None) -> str | None:
    ns_path = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
    if os.path.exists(ns_path):
        with open(ns_path) as f:
            return f.read().strip()
    try:
        contexts, active_context = config.list_kube_config_contexts()
        if context is None:
            return active_context["context"]["namespace"]
        selected_context = next(ctx for ctx in contexts if ctx["name"] == context)
        return selected_context["context"]["namespace"]
    except (KeyError, StopIteration):
        return "default"


# Get the logs from pods with the label 'role'
def get_logs(namespace: str, role: str, log_file_name: str) -> bool:
    with open(log_file_name, "a") as log_file:
        try:
            # List all pods in this namespace with the label 'stable'
            pods = v1.list_namespaced_pod(
                namespace=namespace, label_selector=f"role={role}"
            )
            if not pods.items:
                print(f"No pods found for role {role} in namespace {namespace}")
                return 1
            for pod in pods.items:
                pod_name = pod.metadata.name
                namespace = pod.metadata.namespace
                print(
                    f"Getting logs for {role} pod {pod_name} in namespace {namespace}"
                )
                response = v1.read_namespaced_pod_log(
                    name=pod_name, namespace=namespace
                )

                # Write the response text to the log file
                log_file.write(f"Pod: {pod_name}\n{response}\n")
                print(f"Got logs for pod {pod_name}")
                return 0
        except requests.RequestException as e:
            print(f"Error: {e}")
            # If an error occurs, write the error to the log file
            log_file.write(str(e) + "\n")
            return 1
        except client.exceptions.ApiException as e:
            print(f"API Error: {e}")
            # If an API error occurs, write the error to the log file
            log_file.write(str(e) + "\n")
            return 1


# get current namespace from kubeconfig
namespace = get_current_namespace(context="default")  # TODO
if not namespace:
    print("Namespace not found")
    sys.exit(1)
print(f"Current namespace: {namespace}")

if get_logs(namespace, "stable", log_stable_file_name) != 0:
    sys.exit(1)
if not get_logs(namespace, "canary", log_canary_file_name):
    sys.exit(1)

# # Get the logs from stable pods
# with open(log_file_name_stable, "a") as log_file:
#     try:
#         # get pods logs

#         # Write the response text to the log file
#         print(f"Got stable logs")
#         log_file.write(f"{response.status_code} {response.text}\n")
#     except requests.RequestException as e:
#         return_code = 1
#         print(f"Error: {e}")
#         # If an error occurs, write the error to the log file
#         log_file.write(str(e) + "\n")
#     # Wait for 1 second before making the next request
#     time.sleep(1)

# Get the logs from canary pods

# TODO

# create a model
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest",
    apy_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

system_template = (
    "Analyze what was this canary behavior based on these logs, compare the stable version vs the canary version."
    + "After your analysis, in the last line write a json formatted line with these entries: "
    + "one named 'text' with your analysis text; "
    + "one named 'promote' with 'true' or 'false' depending on whether canary promotion should continue; "
    + "one named 'confidence' with a number from 0 to 100 representing your confidence in the decision. "
    + "The stable version logs start with '--- STABLE LOGS ---' "
    + "and the canary version logs start with '--- CANARY LOGS ---' "
)

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)
parser = StrOutputParser()

# analyze logs using the model
total_cost = 0
print(f"\n\nAnalyzing log files: {log_stable_file_name} and {log_canary_file_name}\n")
with open(log_stable_file_name, "r") as stable_file:
    with open(log_canary_file_name, "r") as canary_file:
        lines_stable = stable_file.readlines()
        lines_canary = canary_file.readlines()
        with get_openai_callback() as cb:
            chain = prompt_template | model | parser
            result = chain.invoke(
                {
                    "text": f"--- STABLE LOGS ---\n{lines_stable}\n\n--- CANARY LOGS ---\n{lines_canary}"
                }
            )
            total_cost += cb.total_cost
            print(f"{result}\n")

# print the cost
print(
    f"Total Cost (USD): ${format(total_cost, '.6f')}"
)  # without specifying the model version, flat-rate 0.002 USD per 1k input and output tokens is used

print(f"Returning code: {return_code}")
sys.exit(return_code)
