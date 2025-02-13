import pandas as pd
import mammoth
from io import BytesIO
import chardet
from typing import Optional
from loguru import logger
import pdfplumber

class FileParser:
    @staticmethod
    def parse_file(file_type: str, file_content: bytes) -> Optional[str]:
        try:
            if file_type == 'application/pdf':
                return FileParser._parse_pdf(file_content)
            elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return FileParser._parse_docx(file_content)
            elif file_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']:
                return FileParser._parse_excel(file_content)
            elif file_type == 'text/csv':
                return FileParser._parse_csv(file_content)
            else:
                raise ValueError(f'不支持的文件类型: {file_type}')
        except Exception as e:
            logger.error(f'文件解析错误: {str(e)}')
            raise

    @staticmethod
    def _parse_pdf(content: bytes) -> str:
        with pdfplumber.open(BytesIO(content)) as pdf:
            return '\n'.join(page.extract_text() for page in pdf.pages)

    @staticmethod
    def _parse_docx(content: bytes) -> str:
        result = mammoth.extract_raw_text({'buffer': content})
        return result.value

    @staticmethod
    def _parse_excel(content: bytes) -> str:
        df = pd.read_excel(BytesIO(content))
        return FileParser._format_dataframe(df)

    @staticmethod
    def _parse_csv(content: bytes) -> str:
        encoding = chardet.detect(content)['encoding'] or 'utf-8'
        df = pd.read_csv(BytesIO(content), encoding=encoding)
        return FileParser._format_dataframe(df)

    @staticmethod
    def _format_dataframe(df: pd.DataFrame) -> str:
        headers = ' | '.join(str(col) for col in df.columns)
        rows = [' | '.join(str(cell) for cell in row) for _, row in df.iterrows()]
        return f"表头:\n{headers}\n\n数据:\n" + '\n'.join(rows)