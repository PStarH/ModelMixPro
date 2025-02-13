# ModelMixSuper

## Introduction
A FastAPI-based proxy server that combines reasoning and execution models into a unified system. Features streaming responses, image recognition, autonomous web search, and automatic failover. Supports OpenAI-compatible API for seamless integration.

## Features

### Hybrid Model Architecture
Utilizes a combination of different AI models to enhance performance and provide diverse functionalities.

### Multimodal Support
Supports both text and image inputs, allowing for versatile applications in various domains.

### High Availability
Designed to ensure continuous operation and minimal downtime, providing reliable access to AI services.

### Intelligent Search Functionality
Incorporates advanced search capabilities to retrieve relevant information efficiently.

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Required libraries (listed in `requirements.txt`)
- An active internet connection for model access

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ModelMixSuper.git
   cd ModelMixSuper
   ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Configuration
- Create a `.env` file in the root directory and configure the necessary environment variables, including API keys and model settings.

### Service Startup Instructions
To start the server, run:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

I'll help you enhance the API usage documentation in the README.md with more detailed and practical examples. Here's how we can update the API section:

```markdown:/Users/sampan/Documents/GitHub/GeminiMixSuper/README.md
## API Usage Instructions

### Base URL
```bash
http://your-server:8000
```

### Authentication
All API endpoints require authentication using a Bearer token:
```bash
Authorization: Bearer YOUR_API_KEY
```

### 1. Text Completion API

#### Endpoint
- **URL:** `/v1/chat/completions`
- **Method:** POST
- **Content-Type:** application/json

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Model to use ("openai" or "gemini") |
| messages | array | Yes | Array of message objects |
| stream | boolean | No | Enable streaming responses (default: true) |
| max_tokens | integer | No | Maximum tokens in response |
| temperature | float | No | Sampling temperature (0.0 to 1.0) |

#### Example Request
```bash
curl -X POST "http://your-server:8000/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai",
    "messages": [
      {
        "role": "user",
        "content": "What is artificial intelligence?"
      }
    ],
    "stream": true
  }'
```

### 2. Image Analysis API

#### Endpoint
- **URL:** `/v1/chat/completions`
- **Method:** POST
- **Content-Type:** application/json

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Must be "image" |
| messages | array | Yes | Array containing image URLs |

#### Single Image Analysis
```bash
curl -X POST "http://your-server:8000/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "image",
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "image_url",
          "image_url": {
            "url": "https://example.com/image.jpg"
          }
        }
      }
    ]
  }'
```

#### Multiple Image Analysis
```bash
curl -X POST "http://your-server:8000/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "image",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "image_url",
            "image_url": {
              "url": "https://example.com/image1.jpg"
            }
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "https://example.com/image2.jpg"
            }
          }
        ]
      }
    ]
  }'
```

### 3. File Management API

#### Upload File
- **URL:** `/files/upload`
- **Method:** POST
- **Content-Type:** multipart/form-data

```bash
curl -X POST "http://your-server:8000/files/upload" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@/path/to/your/file.pdf"
```

#### List Files
- **URL:** `/files/list`
- **Method:** GET

```bash
curl "http://your-server:8000/files/list" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### Delete File
- **URL:** `/files/{filename}`
- **Method:** DELETE

```bash
curl -X DELETE "http://your-server:8000/files/your-file.pdf" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 4. Model Configuration API

#### Update Model Configuration
- **URL:** `/config/model`
- **Method:** POST
- **Content-Type:** multipart/form-data

```bash
curl -X POST "http://your-server:8000/config/model" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "model_name=gemini" \
  -F "api_key=YOUR_MODEL_API_KEY" \
  -F "base_url=https://api.example.com"
```

#### Get Available Models
- **URL:** `/config/models`
- **Method:** GET

```bash
curl "http://your-server:8000/config/models" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Response Formats

#### Success Response
```json
{
  "id": "chat-12345",
  "object": "chat.completion",
  "created": 1677858242,
  "model": "openai",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Response content here"
      },
      "finish_reason": "stop"
    }
  ]
}
```

#### Error Response
```json
{
  "error": {
    "message": "Error description",
    "type": "error_type",
    "code": 400
  }
}
```

### Rate Limiting
- Default rate limit: 60 requests per minute
- Exceeded rate limit response: HTTP 429 (Too Many Requests)

### Best Practices
1. Always handle API errors gracefully
2. Implement retry logic for failed requests
3. Use streaming for long responses
4. Keep API keys secure and rotate them regularly
5. Monitor API usage and response times

## Notes

### Important Points About Image Data
- Ensure images are accessible via public URLs.
- Supported image formats include JPEG, PNG, and GIF.

### Stream Settings
- Streaming responses are available for real-time interactions.

### API Key Requirements
- An API key is required for authentication. Ensure to include it in the request headers.

### Image Recognition Process
- The server processes images using advanced AI models to extract relevant information and insights.

## Development Plan

- [ ] Support more model combinations
- [ ] Add automatic model selection feature
- [ ] Optimize image recognition performance
- [ ] Add more error handling mechanisms
- [ ] Implement OCR processing for PDF and images
  - PDF text extraction with layout preservation
  - Image text recognition
  - Multi-language OCR support
- [ ] Add audio processing with Whisper
  - Audio transcription
  - Multi-language support
  - Real-time transcription capability
- [ ] Develop web interface
  - Chat interface
  - File management
  - System settings
- [ ] Enhance file processing capabilities
  - Batch processing
  - Format conversion
  - Result preview