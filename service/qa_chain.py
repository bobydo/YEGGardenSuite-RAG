from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from config import GEN_MODEL, LLM_KWARGS
from service.prompts import CHAT_PROMPT

def make_llm():
    return OllamaLLM(model=GEN_MODEL, **LLM_KWARGS)

def make_prompt():
    # CHAT_PROMPT already includes system + human message templates
    return CHAT_PROMPT

def make_qa(vs):
    retriever = vs.as_retriever(search_kwargs={"k": 4})
    llm = make_llm()
    prompt = make_prompt()
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )
