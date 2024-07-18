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

# read .env variables
load_dotenv()

# if /logs exists use it, otherwise use app.log
log_file_name = "/logs/app.log" if os.path.exists("/logs") else "app.log"

# first argument is service url
url = sys.argv[1] if len(sys.argv) > 1 else None
if not url:
    print("Please provide the url as an argument.")
    sys.exit(1)

# initial sleep
sleep = 1
print(f"Sleeping for {sleep} seconds")
time.sleep(sleep)

return_code = 0

# Open the log file
with open(log_file_name, "a") as log_file:
    for i in range(10):  # Loop 10 times
        try:
            # Make the request with a timeout of 1 second
            print(f"Making request {i + 1} to {url}")
            response = requests.get(url, timeout=1)
            if response.status_code != 200:
                return_code = 1
            # Write the response text to the log file
            print(f"Response: {response.status_code} {response.text}")
            log_file.write(f"{response.status_code} {response.text}\n")
        except requests.RequestException as e:
            return_code = 1
            print(f"Error: {e}")
            # If an error occurs, write the error to the log file
            log_file.write(str(e) + "\n")
        # Wait for 1 second before making the next request
        time.sleep(1)

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

system_template = "Analyze what was this canary behavior based on this curl output:"

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)
parser = StrOutputParser()

# analyze each log file

total_cost = 0
print(f"\n\nAnalyzing log file: {log_file_name}\n")
with open(log_file_name, "r") as f:
    lines = f.readlines()
    with get_openai_callback() as cb:
        chain = prompt_template | model | parser
        result = chain.invoke({"text": lines})
        total_cost += cb.total_cost
        print(f"{result}\n")

# print the cost
print(
    f"Total Cost (USD): ${format(total_cost, '.6f')}"
)  # without specifying the model version, flat-rate 0.002 USD per 1k input and output tokens is used

print(f"Returning code: {return_code}")
sys.exit(return_code)
