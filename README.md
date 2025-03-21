# PDF Processing API

A FastAPI backend service for processing PDF documents and extracting markdown content using docling. The service stores both the original PDF and the extracted markdown content in Google Cloud Storage.

## Features

- PDF file upload endpoint
- Document listing with filtering and pagination
- Automatic markdown extraction using docling
- Google Cloud Storage integration for file storage
- Health check endpoint

## Setup

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Set up Google Cloud Storage:
   - Create a Google Cloud project
   - Create a storage bucket
   - Generate a service account key with Storage Admin permissions
   - Download the service account key JSON file

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration:
     - Set `GCS_BUCKET_NAME` to your Google Cloud Storage bucket name
     - Set `GOOGLE_APPLICATION_CREDENTIALS` to the path of your service account key JSON file

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

### POST /upload/
Upload a PDF file for processing. The endpoint will:
- Store the original PDF in Google Cloud Storage
- Extract markdown content using docling
- Store the markdown in Google Cloud Storage
- Return URLs for both files

Example response:
```json
{
    "message": "Document processed successfully",
    "document_id": "uuid",
    "pdf_url": "https://storage.googleapis.com/bucket/pdfs/uuid.pdf",
    "markdown_url": "https://storage.googleapis.com/bucket/markdown/uuid.md"
}
```

### GET /documents/
List processed documents stored in the bucket. Returns both PDF and markdown URLs for each document.

Query Parameters:
- `limit` (optional): Maximum number of documents to return (default: 50, max: 100)
- `prefix` (optional): Filter documents by prefix

Example response:
```json
[
    {
        "document_id": "uuid",
        "pdf_url": "https://storage.googleapis.com/bucket/pdfs/uuid.pdf",
        "markdown_url": "https://storage.googleapis.com/bucket/markdown/uuid.md",
        "created_at": "2024-02-20T10:30:00Z",
        "size_bytes": 1234567
    }
]
```

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