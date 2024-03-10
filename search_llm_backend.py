# -*- coding: utf-8 -*-
import os
from loguru import logger
import requests
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

GOOGLE_SEARCH_API = os.environ['GOOGLE_SEARCH_API']
GOOGLE_ENGINE_ID = os.environ['GOOGLE_ENGINE_ID']
GOOGLE_SEARCH_ENDPOINT='https://www.googleapis.com/customsearch/v1?'

query='why we need python'
params = {
    "key": GOOGLE_SEARCH_API,
    "cx": GOOGLE_ENGINE_ID,
    "q": query,
}
response = requests.get(
    GOOGLE_SEARCH_ENDPOINT, params=params, timeout=5
)
if not response.ok:
    logger.error(f"{response.status_code} {response.text}")
json_content = response.json()

# I user gemini api. It input token limit	30720,so context cannot exceed this limit
contexts = json_content["items"][:3]

# adopted  search_with_lepton promot
_rag_query_text = """
You are a large language AI assistant built by Lepton AI. You are given a user question, and please write clean, concise and accurate answer to the question. You will be given a set of related contexts to the question, each starting with a reference number like [[citation:x]], where x is a number. Please use the context and cite the context at the end of each sentence if applicable.

Your answer must be correct, accurate and written by an expert using an unbiased and professional tone. Please limit to 1024 tokens. Do not give any information that is not related to the question, and do not repeat. Say "information is missing on" followed by the related topic, if the given context do not provide sufficient information.

Please cite the contexts with the reference numbers, in the format [citation:x]. If a sentence comes from multiple contexts, please list all applicable citations, like [citation:3][citation:5]. Other than code and specific names and citations, your answer must be written in the same language as the question.

Here are the set of contexts:

{context}

Remember, don't blindly repeat the contexts verbatim. And here is the user question:
"""
system_prompt = _rag_query_text.format(
    context="\n\n".join(
        [f"[[citation:{i+1}]] {c['snippet']}" for i, c in enumerate(contexts)]
    )
)


GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
import google.generativeai as genai
genai.configure(api_key=GOOGLE_API_KEY,transport='rest')
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content(system_prompt + query)
print('=====',response.text)