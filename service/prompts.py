from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from config import SYSTEM_RULES

# Central chat prompt for QA. History placeholder is optional.
CHAT_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(SYSTEM_RULES),
    MessagesPlaceholder(variable_name="history", optional=True),
    HumanMessagePromptTemplate.from_template(
        "Question: {question}\n\nContext:\n{context}\n\nAnswer:"),
])

__all__ = ["CHAT_PROMPT"]
