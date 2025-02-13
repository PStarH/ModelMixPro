from typing import List, Dict, Any, Optional
from fastapi import UploadFile
from pathlib import Path
import aiofiles
import os
from loguru import logger

class FileHandler:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
    async def save_file(self, file: UploadFile) -> Dict[str, Any]:
        """保存上传的文件"""
        try:
            file_path = self.upload_dir / file.filename
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            return {
                "filename": file.filename,
                "path": str(file_path),
                "size": len(content)
            }
        except Exception as e:
            logger.error(f"文件保存失败: {str(e)}")
            raise
    
    async def list_files(self) -> List[Dict[str, Any]]:
        """列出所有上传的文件"""
        try:
            files = []
            for file_path in self.upload_dir.glob("*"):
                if file_path.is_file():
                    files.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size": file_path.stat().st_size
                    })
            return files
        except Exception as e:
            logger.error(f"获取文件列表失败: {str(e)}")
            raise
    
    async def delete_file(self, filename: str) -> bool:
        """删除指定文件"""
        try:
            file_path = self.upload_dir / filename
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"删除文件失败: {str(e)}")
            raise