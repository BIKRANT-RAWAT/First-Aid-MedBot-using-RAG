## Importing required libraries

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader




## fuction to load pdf files
def load_pdf(file_path):
    loader= DirectoryLoader(
        file_path,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )

    documents=loader.load()
    return documents


## fuction to filter

def filter_min_doc(docs:List[Document]) -> List[Document]:
    min_docs:List[Document]=[]
    for doc in docs:
        src=doc.metadata.get("source")
        min_docs.append(
            Document(
                page_content=doc.page_content,
                metadata={"source":src}
                    )
        )
    return min_docs


## function to chunk
def text_splitter(minimal_docs):
    text_splitter= RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=20
    )

    text_chuck= text_splitter.split_documents(minimal_docs)
    return text_chuck


## function to download HFmodel and return embeddings
def download_embeddings():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name
    )
    return embeddings