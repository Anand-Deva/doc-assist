# Langchain Document Helper Bot

A Streamlit-based application that helps you analyze and chat with your PDF documents using LangChain and OpenAI's GPT models.

## Features

- 🔒 Secure OpenAI API key handling with validation
- 📄 PDF document upload and processing
- 💬 Interactive chat interface
- 🔍 Intelligent document analysis
- 🎯 Context-aware responses
- 🔄 Chat history tracking
- 📁 Persistent storage for documents and indexes

## Prerequisites

Before running the application, you'll need:

1. Docker installed on your system
2. An OpenAI API key (get it from [OpenAI's platform](https://platform.openai.com/account/api-keys))

## Quick Start with Docker

### Building the Docker Image

```bash
# Clone the repository
git clone <repository-url>
cd doc-assist

# Build the Docker image
docker build -t doc-assist .
```

### Running the Application

```bash
# Create directories for persistent storage
mkdir -p ./data/uploads ./data/indexes

# Run the container with volume mounts
docker run -p 8501:8501 \
  -v $(pwd)/data/uploads:/app/data/uploads \
  -v $(pwd)/data/indexes:/app/data/indexes \
  doc-assist
```

After running these commands, access the application at: http://localhost:8501

## Directory Structure

```
doc-assist/
├── data/
│   ├── uploads/    # Directory for uploaded PDF files
│   └── indexes/    # Directory for FAISS indexes
├── streamlit.py    # Main application file
├── document_handler.py  # Document processing logic
├── requirements.txt
├── Dockerfile
└── README.md
```

## Usage Instructions

1. When you first open the application, you'll be prompted to enter your OpenAI API key
2. The application will validate your API key before allowing document uploads
3. After entering a valid API key, you can upload your PDF document
4. Once a document is uploaded, you can start asking questions about its contents
5. The application will provide answers based on the document's content

## Development Setup

If you want to run the application without Docker:

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create necessary directories:
```bash
mkdir -p ./data/uploads ./data/indexes
```

4. Run the application:
```bash
streamlit run streamlit.py
```

## Environment Variables

The application uses the following environment variables:

- `UPLOAD_DIR`: Directory for storing uploaded files (default: /app/data/uploads)
- `INDEX_STORE_DIR`: Directory for storing FAISS indexes (default: /app/data/indexes)
- `PORT`: The port on which Streamlit runs (default: 8501)
- `PYTHONUNBUFFERED`: Set to 1 for unbuffered output
- `PYTHONDONTWRITEBYTECODE`: Set to 1 to prevent Python from writing bytecode files

## Security Notes

- The application validates OpenAI API keys before use
- API keys are handled securely in memory only
- All uploaded files are stored in a dedicated directory
- Automatic cleanup of temporary files
- The Docker container runs as a non-root user (UID 1000)
- Proper directory permissions are set during container build

## Troubleshooting

### Common Issues

1. **Docker Build Fails**
   - Ensure you have the latest version of Docker installed
   - Check if you have sufficient disk space
   - Make sure all required files are present in the directory

2. **Application Can't Start**
   - Verify that port 8501 is not in use by another application
   - Check if Docker is running on your system
   - Ensure the data directories have proper permissions

3. **PDF Upload Issues**
   - Ensure your PDF is not corrupted
   - Check if the PDF is not password protected
   - Verify write permissions in the uploads directory

4. **API Key Issues**
   - Make sure your API key starts with 'sk-'
   - Ensure your API key is valid and active
   - Check your internet connection for API validation

### Error Messages

- "Invalid API key": Ensure your OpenAI API key is valid and properly formatted
- "Error creating upload directory": Check directory permissions
- "Please upload a document first!": Upload a PDF document before asking questions
- "Error generating response": Check your API key and internet connection

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

```
Copyright 2024 Doc-Assist

Licensed under the Apache License, Version 2.0;
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

For the full license text, see the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). 