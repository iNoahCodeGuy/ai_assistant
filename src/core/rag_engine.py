from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.document_loaders import CSVLoader
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
import os

class RAGEngine:
    def __init__(self, career_kb_path, code_index_path):
        self.career_kb_path = career_kb_path
        self.code_index_path = code_index_path
        
        self.embeddings = OpenAIEmbeddings()
        self.career_kb = self.load_career_kb()
        self.code_index = self.load_code_index()
        
        self.memory = ConversationBufferMemory()
        self.retrieval_qa = RetrievalQA.from_chain_type(
            llm=OpenAI(),
            chain_type="stuff",
            retriever=self.create_retriever()
        )

    def load_career_kb(self):
        loader = CSVLoader(self.career_kb_path)
        return loader.load()

    def load_code_index(self):
        # Implement code index loading logic here
        pass

    def create_retriever(self):
        career_store = FAISS.from_documents(self.career_kb, self.embeddings)
        # Assuming code_index is also a FAISS store
        code_store = FAISS.from_documents(self.code_index, self.embeddings)
        return career_store.as_retriever()  # Modify as needed to combine both stores

    def query(self, user_input):
        self.memory.add(user_input)
        response = self.retrieval_qa.run(user_input)
        self.memory.add(response)
        return response

    def get_memory_summary(self):
        return self.memory.get_summary()