import os
import requests
import sys

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureChatOpenAI
from langchain_community.callbacks import get_openai_callback
from dotenv import load_dotenv

# read .env variables
load_dotenv()

# first argument is a file name
file = sys.argv[1] if len(sys.argv) > 1 else None
if not file:
    print("Please provide a file name as an argument.")
    sys.exit(1)

# create a model
model = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
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
print(f"Analyzing log file: {file}")
with open(file, "r") as f:
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

