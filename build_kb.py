import os
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

def load_knowledge_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    sections = re.split(r'\n\s*\n', raw_text)
    documents = []
    for i, section in enumerate(sections):
        if section.strip():
            lines = section.strip().split('\n')
            title = lines[0] if lines else f"Section {i}"
            documents.append(Document(
                page_content=section,
                metadata={"source": "knowledge.txt", "chunk_id": i, "topic": title[:50]}
            ))
    return documents

def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30,
        separators=["\n\n", "\n", ". ", " "],
        length_function=len
    )
    return splitter.split_documents(documents)

if __name__ == "__main__":
    docs = load_knowledge_from_file("knowledge.txt")
    chunked = chunk_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(
        documents=chunked,
        embedding=embeddings,
        persist_directory="./chroma_db",
        collection_name="secure_coding"
    )
    vectorstore.persist()
    print(f"✅ Vector store built with {len(chunked)} chunks")
