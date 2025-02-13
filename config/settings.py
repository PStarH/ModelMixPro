import os
from dotenv import load_dotenv

# 加载 .env 文件中的配置
load_dotenv()

class ThinkingModelSettings:
    # 思考大模型（用于前置思考）的配置
    DEEPSEEK_R1_API_KEY = os.getenv('DEEPSEEK_R1_API_KEY')
    DEEPSEEK_R1_MODEL = os.getenv('DEEPSEEK_R1_MODEL')
    DEEPSEEK_R1_MAX_TOKENS = int(os.getenv('DEEPSEEK_R1_MAX_TOKENS', 7985))
    DEEPSEEK_R1_TEMPERATURE = float(os.getenv('DEEPSEEK_R1_TEMPERATURE', 0.7))
    # 支持推理的思考模型列表
    SUPPORTED_THINKING_MODELS = ['deepseek_r1', 'o3-mini', 'o1-mini', 'o1-preview', 'o1']

class OutputModelSettings:
    # 普通输出大模型（用于主要回答）的配置
    Model_output_API_KEY = os.getenv('Model_output_API_KEY')
    Model_output_MODEL = os.getenv('Model_output_MODEL')
    Model_output_MAX_TOKENS = int(os.getenv('Model_output_MAX_TOKENS', 7985))
    Model_output_TEMPERATURE = float(os.getenv('Model_output_TEMPERATURE', 0.4))
    Model_output_WebSearch = os.getenv('Model_output_WebSearch') == 'True'

class Settings:
    # 代理设置
    PROXY_URL = os.getenv('PROXY_URL')
    PROXY_PORT = int(os.getenv('PROXY_PORT', 4120))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
    REQUEST_MAX_REDIRECTS = int(os.getenv('REQUEST_MAX_REDIRECTS', 5))
    
    # OpenAI 和 Anthropic 等其他模型的配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', 8192))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.7))
    
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-3')
    ANTHROPIC_MAX_TOKENS = int(os.getenv('ANTHROPIC_MAX_TOKENS', 8192))
    ANTHROPIC_TEMPERATURE = float(os.getenv('ANTHROPIC_TEMPERATURE', 0.7))
    
    # 第三方及自定义模型配置
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')
    OLLAMA_API_KEY = os.getenv('OLLAMA_API_KEY')
    
    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
    MISTRAL_MODEL = os.getenv('MISTRAL_MODEL', 'mistral-7b')
    MISTRAL_BASE_URL = os.getenv('MISTRAL_BASE_URL')
    
    QWEN_API_KEY = os.getenv('QWEN_API_KEY')
    QWEN_MODEL = os.getenv('QWEN_MODEL', 'qwen-14b')
    QWEN_BASE_URL = os.getenv('QWEN_BASE_URL')
    
    CUSTOM_MODEL_API_KEY = os.getenv('CUSTOM_MODEL_API_KEY')
    CUSTOM_MODEL_BASE_URL = os.getenv('CUSTOM_MODEL_BASE_URL')
    CUSTOM_MODEL_NAME = os.getenv('CUSTOM_MODEL_NAME', 'custom-model')
    
    IMAGE_MODEL_API_KEY = os.getenv('IMAGE_MODEL_API_KEY')
    IMAGE_MODEL = os.getenv('IMAGE_MODEL')
    IMAGE_MODEL_PROMPT = os.getenv('IMAGE_MODEL_PROMPT')
    
    GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')
    GOOGLE_SEARCH_PROMPT = os.getenv('GOOGLE_SEARCH_PROMPT')
    
    RELAY_PROMPT = os.getenv('RELAY_PROMPT')
    HYBRID_MODEL_NAME = os.getenv('HYBRID_MODEL_NAME', 'GeminiMIXR1')
    OUTPUT_API_KEY = os.getenv('OUTPUT_API_KEY')
    
    # 实例化模型设置
    thinking_model_settings = ThinkingModelSettings()
    output_model_settings = OutputModelSettings()

# 生成全局设置实例
settings = Settings()
