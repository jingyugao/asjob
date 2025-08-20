#!/usr/bin/env python3
"""调试配置系统 - 简化版本"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent

print(f"=== 调试信息 ===")
print(f"当前工作目录: {os.getcwd()}")
print(f"脚本所在目录: {Path(__file__).parent}")
print(f"项目根目录: {PROJECT_ROOT}")
print(f".env文件路径: {PROJECT_ROOT / '.env'}")
print(f".env文件是否存在: {(PROJECT_ROOT / '.env').exists()}")

# 读取.env文件内容
env_file_path = PROJECT_ROOT / ".env"
if env_file_path.exists():
    with open(env_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"\n.env文件内容:")
        print(content)

class SimpleLLMSettings(BaseSettings):
    """简化的LLM配置"""
    api_key: str = ""
    
    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=str(env_file_path),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

print(f"\n=== 测试配置类 ===")
try:
    # 设置环境变量
    os.environ["LLM_GOOGLE_API_KEY"] = "test_key_from_env"
    
    test_settings = SimpleLLMSettings()
    print(f"SimpleLLMSettings.api_key: {repr(test_settings.api_key)}")
    print(f"环境变量LLM_GOOGLE_API_KEY: {os.getenv('LLM_GOOGLE_API_KEY')}")
    
    # 清理环境变量
    del os.environ["LLM_GOOGLE_API_KEY"]
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
