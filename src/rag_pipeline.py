import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

class KnowledgeBaseRAG:
    """Secure Coding Knowledge Base and RAG Pipeline Module using free local embeddings."""

    def __init__(self, kb_path: str = "knowledge_base/owasp_guidelines.md", persist_directory: str = "./chroma_db"):
        self.kb_path = kb_path
        self.persist_directory = persist_directory
        # Runs 100% free locally without any API key
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = None

    def initialize_knowledge_base(self):
        """Indexes secure coding guidelines into ChromaDB via chunking and embedding."""
        if not os.path.exists(self.kb_path):
            raise FileNotFoundError(f"Knowledge base document not found at {self.kb_path}")

        loader = TextLoader(self.kb_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)

        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        return self.vector_store

    def query_knowledge_base(self, query: str, k: int = 3):
        if not self.vector_store:
            self.vector_store = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
        docs = self.vector_store.similarity_search(query, k=k)
        return docs
