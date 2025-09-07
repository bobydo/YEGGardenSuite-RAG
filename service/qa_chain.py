from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from config import GEN_MODEL, SYSTEM_RULES, QA_TEMPLATE, LLM_KWARGS

def make_llm():
    return OllamaLLM(model=GEN_MODEL, **LLM_KWARGS)

def make_prompt():
    return PromptTemplate(
        template=QA_TEMPLATE,
        input_variables=["question", "context"],
        partial_variables={"system": SYSTEM_RULES},
    )

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
