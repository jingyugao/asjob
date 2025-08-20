#!/usr/bin/env python3
"""调试配置系统"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class TestLLMSettings(BaseSettings):
    """测试LLM配置"""
    api_key: str = ""
    
    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

print("=== 环境变量调试 ===")
print(f"当前工作目录: {os.getcwd()}")
print(f".env文件是否存在: {os.path.exists('.env')}")

# 检查所有LLM_开头的环境变量
llm_env_vars = {k: v for k, v in os.environ.items() if k.startswith('LLM_')}
print(f"LLM_环境变量: {llm_env_vars}")

# 检查GOOGLE_API_KEY环境变量
print(f"GOOGLE_API_KEY环境变量: {os.getenv('GOOGLE_API_KEY', '未设置')}")

print("\n=== 测试配置类 ===")
try:
    test_settings = TestLLMSettings()
    print(f"TestLLMSettings.api_key: {repr(test_settings.api_key)}")
except Exception as e:
    print(f"TestLLMSettings错误: {e}")

print("\n=== 直接读取.env文件 ===")
try:
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
        print("环境变量内容:")
        for line in lines:
            print(f"  {line}")
except Exception as e:
    print(f"读取.env文件错误: {e}")
