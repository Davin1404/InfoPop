import os
import json
from typing import List, Optional
from fastapi import HTTPException
from pydantic import BaseModel

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from datetime import datetime

class ModelConfig(BaseModel):
    name: str
    display_name: str
    api_key_env: str
    base_url: Optional[str] = None
    model_type: str = "openai"

class AIService:
    def __init__(self, model_config_file: str):
        self.model_config_file = model_config_file
    
    def load_model_configs(self) -> List[ModelConfig]:
        """Load model configurations from JSON file"""
        try:
            if os.path.exists(self.model_config_file):
                with open(self.model_config_file, 'r', encoding='utf-8') as f:
                    configs = json.load(f)
                    return [ModelConfig(**config) for config in configs]
        except Exception as e:
            pass
        
        # Default configurations if file doesn't exist
        return [
            ModelConfig(
                name="gpt-3.5-turbo",
                display_name="GPT-3.5 Turbo",
                api_key_env="OPENAI_API_KEY",
                model_type="openai"
            ),
            ModelConfig(
                name="gpt-4",
                display_name="GPT-4",
                api_key_env="OPENAI_API_KEY",
                model_type="openai"
            )
        ]
    
    def get_model_config(self, model_name: str) -> ModelConfig:
        """Get model configuration by name"""
        configs = self.load_model_configs()
        
        # Find the model config
        for config in configs:
            if config.name == model_name:
                return config
        
        # Default to gpt-3.5-turbo if model not found
        return ModelConfig(
            name="gpt-3.5-turbo",
            display_name="GPT-3.5 Turbo",
            api_key_env="OPENAI_API_KEY",
            model_type="openai"
        )
    
    def get_chat_model(self, model_name: str) -> BaseChatModel:
        """Get the appropriate chat model based on configuration"""
        model_config = self.get_model_config(model_name)
        
        # Get API key from environment
        api_key = os.getenv(model_config.api_key_env)
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail=f"API key not found for {model_config.display_name}. Please set {model_config.api_key_env} environment variable."
            )
        
        # Create the model instance
        if model_config.model_type == "openai":
            model_kwargs = {
                "model": model_config.name,
                "api_key": api_key,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            if model_config.base_url:
                model_kwargs["base_url"] = model_config.base_url
            
            return ChatOpenAI(**model_kwargs)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported model type: {model_config.model_type}"
            )
    
    def handle_ai_error(self, error: Exception, model_name: str) -> HTTPException:
        """Handle AI model errors and return appropriate HTTP exceptions"""
        error_str = str(error)
        
        # 针对不同的错误提供更友好的错误信息
        if "401" in error_str or "invalid_api_key" in error_str.lower():
            return HTTPException(
                status_code=401, 
                detail=f"API密钥无效，请检查 {model_name} 的API密钥配置"
            )
        elif "402" in error_str or "insufficient_quota" in error_str.lower():
            return HTTPException(
                status_code=402, 
                detail=f"账户余额不足或配额用完，请检查 {model_name} 的账户状态和余额"
            )
        elif "429" in error_str or "rate_limit" in error_str.lower():
            return HTTPException(
                status_code=429, 
                detail=f"请求频率过高，请稍后再试"
            )
        elif "500" in error_str or "internal_server_error" in error_str.lower():
            return HTTPException(
                status_code=500, 
                detail=f"AI服务暂时不可用，请稍后重试"
            )
        else:
            return HTTPException(
                status_code=500, 
                detail=f"AI模型调用失败: {error_str}"
            )
    
    async def test_model(self, model_name: str) -> dict:
        """Test if a specific model is working"""
        try:
            # Get the chat model
            chat_model = self.get_chat_model(model_name)
            
            # Send a simple test message
            test_message = [HumanMessage(content="Say 'Hello' in response")]
            
            # Get AI response
            ai_response = await chat_model.ainvoke(test_message)
            
            return {
                "status": "success",
                "model": model_name,
                "response": ai_response.content,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "model": model_name,
                "error": str(e),
                "timestamp": datetime.now()
            }
