from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any
from loguru import logger
import asyncio
import json
import httpx

from config.settings import settings
from modules.web_parser import WebParser
from modules.image_processor import ImageProcessor
from modules.file_parser import FileParser
from modules.model_handler import ModelHandler
from modules.file_handler import FileHandler
from utils.helpers import format_sse_message, sanitize_content

# 配置日志
logger.add(
    "logs/app.log",
    rotation="1 MB",
    retention="10 days",
    level="INFO"
)

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化组件
web_parser = WebParser()
image_processor = ImageProcessor()
file_parser = FileParser()
model_handler = ModelHandler()
file_handler = FileHandler()

class Message(BaseModel):
    role: str
    content: Union[str, List[Dict[str, Any]]]

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: bool = True
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

async def verify_api_key(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")
    
    api_key = auth_header.split(" ")[1]
    if api_key != settings.OUTPUT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    if request.model == "openai":
        return StreamingResponse(
            model_handler.call_openai(request.messages, request.stream),
            media_type="text/event-stream"
        )
    elif request.model == "gemini":
        return StreamingResponse(
            model_handler.call_gemini(request.messages, request.stream),
            media_type="text/event-stream"
        )
    else:
        raise HTTPException(status_code=400, detail=f"Model not supported: {request.model}")
    try:
        # 预处理消息
        messages = await web_parser.preprocess_messages(request.messages)
        
        # 并行处理图片和搜索
        image_content, search_results = await asyncio.gather(
            process_images(messages),
            perform_search_if_needed(messages)
        )
        
        # 准备发送给模型的消息
        model_messages = prepare_model_messages(messages, image_content, search_results)
        
        # 创建流式响应
        return StreamingResponse(
            model_handler.stream_response(model_messages, request),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_images(messages):
    if image_processor.has_new_images(messages):
        images = image_processor.extract_last_images(messages)
        image_descriptions = await asyncio.gather(*[
            image_processor.process_image(img) for img in images
        ])
        return "\n".join(desc for desc in image_descriptions if desc)
    return None

async def perform_search_if_needed(messages):
    if await model_handler.determine_if_search_needed(messages):
        return await model_handler.perform_web_search(messages)
    return None

def prepare_model_messages(messages, image_content, search_results):
    return [
        *messages,
        *(
            [{"role": "system", "content": f"{settings.GoogleSearch_Send_PROMPT}{search_results}"}]
            if search_results else []
        ),
        *(
            [{"role": "system", "content": f"{settings.Image_SendR1_PROMPT}{image_content}"}]
            if image_content else []
        ),
        {"role": "system", "content": settings.RELAY_PROMPT}
    ]

# 文件上传相关路由
@app.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        result = await file_handler.save_file(file)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/list")
async def list_files():
    try:
        files = await file_handler.list_files()
        return JSONResponse(content=files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    try:
        success = await file_handler.delete_file(filename)
        if success:
            return JSONResponse(content={"message": f"文件 {filename} 已删除"})
        raise HTTPException(status_code=404, detail=f"文件 {filename} 不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 模型配置相关路由
@app.post("/config/model")
async def update_model_config(
    model_name: str = Form(...),
    api_key: str = Form(...),
    base_url: Optional[str] = Form(None)
):
    try:
        # 更新模型配置
        if model_name == "deepseek_r1":
            settings.DEEPSEEK_R1_API_KEY = api_key
            if base_url:
                settings.PROXY_URL = base_url
        elif model_name == "gemini":
            settings.Model_output_API_KEY = api_key
            if base_url:
                settings.PROXY_URL2 = base_url
        elif model_name == "image":
            settings.Image_Model_API_KEY = api_key
            if base_url:
                settings.PROXY_URL3 = base_url
        else:
            raise HTTPException(status_code=400, detail=f"不支持的模型类型: {model_name}")
            
        return JSONResponse(content={"message": f"模型 {model_name} 配置已更新"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/models")
async def get_available_models():
    return JSONResponse(content={
        "models": [
            {
                "name": "deepseek_r1",
                "description": "DeepSeek R1 模型",
                "current_api_key": settings.DEEPSEEK_R1_API_KEY is not None,
                "base_url": settings.PROXY_URL
            },
            {
                "name": "gemini",
                "description": "Gemini 模型",
                "current_api_key": settings.Model_output_API_KEY is not None,
                "base_url": settings.PROXY_URL2
            },
            {
                "name": "image",
                "description": "图像处理模型",
                "current_api_key": settings.Image_Model_API_KEY is not None,
                "base_url": settings.PROXY_URL3
            }
        ]
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.PROXY_PORT)