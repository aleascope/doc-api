# Document Processing API

A FastAPI service that processes PDF documents and:
- converts them to markdown format using Docling
- stores them (along with markdown version) in a Google Cloud Storage bucket

## Features

- PDF document upload and processing
- Automatic conversion to markdown using docling
- Storage in Google Cloud Storage
- Document listing and retrieval
- Health check endpoint

## Setup

1. Install dependencies:
```bash
pip install fastapi uvicorn python-multipart google-cloud-storage python-dotenv docling
```

2. Create a `.env` file in the root directory:

3. Set up Google Cloud Storage:
   - Create a Google Cloud project
   - Create a storage bucket
   - Generate a service account key with Storage Admin permissions
   - Download the service account key JSON file

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration:
     - Set `GCS_BUCKET_NAME` to your Google Cloud Storage bucket name

## Running the Application

Start the server with Poetry:
```bash
poetry run start
```

Or activate the virtual environment and run directly:
```bash
poetry shell
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Upload Document
```http
POST /upload/
Content-Type: multipart/form-data
```

Example using curl:
```bash
curl -X POST "http://localhost:8000/upload/" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@example.pdf"
```

Example response:
```json
{
    "message": "Document processed successfully",
    "document_id": "550e8400-e29b-41d4-a716-446655440000",
    "pdf_url": "https://storage.googleapis.com/your-bucket/pdfs/550e8400-e29b-41d4-a716-446655440000.pdf",
    "markdown_url": "https://storage.googleapis.com/your-bucket/markdown/550e8400-e29b-41d4-a716-446655440000.md"
}
```

### List Documents
```http
GET /documents/?limit=10&prefix=test
```

Example using curl:
```bash
curl "http://localhost:8000/documents/?limit=10"
```

Example response:
```json
[
    {
        "document_id": "550e8400-e29b-41d4-a716-446655440000",
        "pdf_url": "https://storage.googleapis.com/your-bucket/pdfs/550e8400-e29b-41d4-a716-446655440000.pdf",
        "markdown_url": "https://storage.googleapis.com/your-bucket/markdown/550e8400-e29b-41d4-a716-446655440000.md",
        "created_at": "2024-03-15T10:30:00.000Z",
        "size_bytes": 1234567
    },
    // ... more documents
]
```

### Download PDF
```http
GET /documents/{document_id}/pdf
```

Example using curl:
```bash
curl -O "http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000/pdf"
```

Example using browser:

### GET /health
Health check endpoint to verify the service is running.

## Error Handling

- 400 Bad Request: When a non-PDF file is uploaded
- 500 Internal Server Error: For processing or storage errors

## Security Notes

- Update CORS settings in production to restrict access to your frontend domain
- Ensure your Google Cloud credentials are kept secure
- Consider implementing authentication for the API endpoints in production

## Development

To add new dependencies:
```bash
poetry add package-name
```

To update dependencies:
```bash
poetry update
``` 