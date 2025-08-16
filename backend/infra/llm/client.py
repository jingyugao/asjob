from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage, SystemMessage

# Ollama 本地模型
llm = ChatOllama(
    model="llama2",  # 默认使用 llama2 模型，可以根据需要修改
    base_url="http://localhost:11434",  # Ollama 默认端口
    temperature=0.7,
    timeout=120,
)
