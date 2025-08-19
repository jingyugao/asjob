from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage, SystemMessage
from backend.config import Config

# Ollama 本地模型
llm = ChatOllama(
    model=Config.get_llm_model(),
    base_url=Config.get_llm_base_url(),
    temperature=Config.get_llm_temperature(),
    timeout=Config.get_llm_timeout(),
)


if __name__ == "__main__":
    messages = [
        SystemMessage(content="你是一个有用的助手"),
        HumanMessage(content="你好"),
    ]
    response = llm.invoke(messages)
    print(response.content)
