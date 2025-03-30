import os
from dotenv import load_dotenv
from langchain_openai import OpenAI, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_community.vectorstores.faiss import FAISS
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from typing import List, Any
import hashlib

load_dotenv()

def get_index_path(file_path: str) -> str:
    """Generate a unique path for the FAISS index based on the file content."""
    # Get the directory for storing indexes from environment variable or use a default
    index_dir = os.getenv('INDEX_STORE_DIR', '/app/data/indexes')
    
    # Create the directory if it doesn't exist
    os.makedirs(index_dir, exist_ok=True)
    
    # Generate a unique identifier based on the file path
    file_hash = hashlib.md5(file_path.encode()).hexdigest()
    return os.path.join(index_dir, f"faiss_index_{file_hash}")

def run_llm(prompt, file_path: str, chat_history:List[dict[str,Any]]=[], api_key: str = None):
    """ Uses Facebook AI similarity search for vectoring"""
    # Set the API key
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    loader = PyPDFLoader(file_path=file_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n")
    docs = text_splitter.split_documents(documents=documents)
    
    embeddings = OpenAIEmbeddings()
    
    # Get the index path
    index_path = get_index_path(file_path)
    
    # Create and save the vector store
    vectorstore = FAISS.from_documents(docs, embeddings)
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    vectorstore.save_local(index_path)

    # Load the vector store
    new_vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    retriever = new_vectorstore.as_retriever()
    
    llm = ChatOpenAI(temperature=0, verbose=True)

    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    combine_docs_chain = create_stuff_documents_chain(
                            llm,
                            retrieval_qa_chat_prompt
                        )
    rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")

    history_awarness_retriever = create_history_aware_retriever(
                                    llm=llm,
                                    retriever=retriever,
                                    prompt=rephrase_prompt
                                )
    
    retrieval_chain = create_retrieval_chain(
                            combine_docs_chain=combine_docs_chain,
                            retriever=history_awarness_retriever
                        )
    result = retrieval_chain.invoke(input={"input": prompt, "chat_history":chat_history})

    new_result = {
        "query": result['input'],
        "result": result['answer'],
        "source_documents": result['context'] 
    }

    return new_result

if __name__ == "__main__":
    
    print("Begin the magic!!")

    query="What is ReAct?"
    res = run_llm(query, "ReAct.pdf")

    print(res['result'])
