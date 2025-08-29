from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from typing import List
from langchain_core.documents import Document
import os
from utils_chroma import get_vector_store
from prompt_loader import get_default_system_prompt

def get_retriever():
    vector_store = get_vector_store()
    return vector_store.as_retriever(search_kwargs={"k": 2})

output_parser = StrOutputParser()

# Set up prompts and chains
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])



qa_prompt = ChatPromptTemplate.from_messages([
    ("system", get_default_system_prompt()),
    ("system", "Context: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

def get_custom_qa_prompt(prompt_name: str = "AI_Agent_Prompt"):
    """
    Create a custom QA prompt using a specific prompt configuration
    
    Args:
        prompt_name: Name of the prompt file (without .json extension)
        
    Returns:
        ChatPromptTemplate with the specified prompt
    """
    from prompt_loader import get_system_prompt
    
    return ChatPromptTemplate.from_messages([
        ("system", get_system_prompt(prompt_name)),
        ("system", "Context: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])



def get_rag_chain(model="gpt-3.5-turbo", prompt_name: str = None):
    """
    Create a RAG chain with optional custom prompt
    
    Args:
        model: The language model to use
        prompt_name: Optional prompt configuration name. If None, uses default prompt.
        
    Returns:
        RAG chain with the specified configuration
    """
    llm = ChatOpenAI(model=model)
    retriever = get_retriever()
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    
    # Use custom prompt if specified, otherwise use default
    if prompt_name:
        question_answer_chain = create_stuff_documents_chain(llm, get_custom_qa_prompt(prompt_name))
    else:
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)    
    return rag_chain