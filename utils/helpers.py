from typing import Dict, Any, Union, List
import json

def sanitize_content(content: Union[str, List[Dict[str, Any]], Dict[str, Any]]) -> Union[str, List[Dict[str, Any]], Dict[str, Any]]:
    if isinstance(content, list):
        return [
            {
                **item,
                'image_url': {
                    **item['image_url'],
                    'url': f"{item['image_url']['url'][:20]}...[base64]..."
                }
            } if item.get('type') == 'image_url' and item.get('image_url', {}).get('url')
            else item
            for item in content
        ]
    return content

def format_sse_message(data: Dict[str, Any]) -> str:
    return f"data: {json.dumps(data)}\n\n"