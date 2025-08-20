from langchain.schema import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.config import settings

print(settings.llm.model)
print(settings.llm.api_key)
print(settings.llm.temperature)
print(settings.llm.timeout)


# gemini-2.5-pro
# gemini-2.0-flash-lite


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key=settings.llm.api_key,
    temperature=0.3,
    timeout=settings.llm.timeout,
)


if __name__ == "__main__":
    messages = [
        SystemMessage(
            content="请从用户输入的文本中提取出mysql的链接信息。用json格式返回。返回值包含host,port,user,password,database,charset"
        ),
        HumanMessage(
            content="""doris_yuebai:
    Driver: mysql
    Source: dev:qwer(www.abcd.com:9030)/test_db?charset=utf8mb4&parseTime=True&loc=Local&timeout=5s&readTimeout=60s&writeTimeout=60s
    MaxIdleConns: 10
    MaxOpenConns: 100
    ConnMaxLifetime: 1
    ConnMaxIdleTime: 30
    LogLevel: warning
"""
        ),
    ]
    response = llm.invoke(messages)
    print(response.content)
