from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from src.helper import download_embeddings
from src.prompt import *
from src.safety_check import safety_check
load_dotenv()


# from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from typing import List
# from langchain_core.documents import Document
# from langchain_huggingface import HuggingFaceEmbeddings
# from pinecone import Pinecone
# from pinecone import ServerlessSpec


## Initiating flask

app = Flask(__name__)

## Loading API key 
GEMINI_API_KEY =os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY =os.getenv("PINECONE_API_KEY")

## call embeddings function
embedding= download_embeddings()

## index name
index_name = "first-aid-medbot"

## Load Existing index 

docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embedding
    )

## Setting Retriever
retriever = docsearch.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 4, "fetch_k": 10}
)

## Creating instance of Gemini Model
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", 
    google_api_key=GEMINI_API_KEY)

## prompt template chain

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])


## QA CHAIN 

qa_chain = create_stuff_documents_chain(model, prompt)
rag_chain = create_retrieval_chain(retriever, qa_chain)

## classifing query

def classify_query(query):
    chain = triage_prompt | model
    result = chain.invoke({"input": query}).content.strip()
    return result

## Default Page

@app.route("/")
def index():
    return render_template('medchat.html')


## Getting response

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    query = msg

    # Step 1: Triage
    triage = classify_query(query)

    # Step 2: Retrieve + Generate
    response = rag_chain.invoke({"input": query})
    answer = response.get("answer", "")

    # Step 3: Safety filter
    answer = safety_check(answer)

    # Step 4: Add triage-based guidance
    if triage == "Emergency":
        prefix = "⚠️ This may be a medical emergency. Seek immediate medical help.\n\n"
    elif triage == "Urgent":
        prefix = "⚠️ This may require prompt medical attention.\n\n"
    else:
        prefix = ""

    # Step 5: Final Output
    final_response = {
        "triage": triage,
        "answer": prefix + answer,
        "sources": response.get("context", []),
        "disclaimer": "This is not a medical diagnosis. Consult a qualified doctor."
    }

    return str(final_response["answer"])


## setting up port

if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 8080, debug= True)
