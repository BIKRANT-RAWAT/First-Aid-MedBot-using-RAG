from langchain_pinecone import PineconeVectorStore
from pinecone import ServerlessSpec
from pinecone import Pinecone
import os
from src.helper import load_pdf,filter_min_doc,text_splitter,download_embeddings
from dotenv import load_dotenv
load_dotenv()



## Setting API key
GEMINI_API_KEY =os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY =os.getenv("PINECONE_API_KEY")


##  calling for extrating data
extracted_data=load_pdf("raw_data")

## calling for filteration of data
minimal_docs=filter_min_doc(extracted_data)

## calling for chunking data
text_chunk=text_splitter(minimal_docs)

## calling for creating embeddings
embedding = download_embeddings()

## setting up pinecone
pc= Pinecone(api_key=PINECONE_API_KEY)

index_name = "first-aid-medbot"

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=384,          # your embedding size
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)




## Load pinecone db accordingly

existing_indexes = [searchindex.name for searchindex in pc.list_indexes()]

if index_name not in existing_indexes:
    #create new index 
    

    docsearch = PineconeVectorStore.from_documents(
                                documents=text_chunk,
                                embedding=embedding,
                                index_name=index_name
                                )
else:
    # Load Existing index 
    

    docsearch = PineconeVectorStore.from_existing_index(
                                index_name=index_name,
                                embedding=embedding
                                )
  