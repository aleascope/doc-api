from fastapi import FastAPI, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import storage
from docling.document_converter import DocumentConverter  # Updated import
import os
import uuid
from typing import Dict, List
from datetime import datetime
from pydantic import BaseModel
import tempfile
from dotenv import load_dotenv

load_dotenv()  # This loads .env variables into os.environ

bucket_name = os.getenv("GCS_BUCKET_NAME")

class DocumentInfo(BaseModel):
    """
    Pydantic model for document information response
    """
    document_id: str
    pdf_url: str
    markdown_url: str
    created_at: str
    size_bytes: int

app = FastAPI(
    title="Document Processing API",
    description="API for processing PDF documents and extracting markdown content"
)

# Configure CORS to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Update this with specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google Cloud Storage client
storage_client = storage.Client()

@app.post("/upload/", response_model=Dict[str, str])
async def upload_document(file: UploadFile):
    """
    Upload and process a PDF document
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Generate unique ID for the document
        doc_id = str(uuid.uuid4())
        
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            content = await file.read()
            temp_pdf.write(content)
            temp_pdf.flush()
            
            # Process with docling using DocumentConverter
            converter = DocumentConverter()
            result = converter.convert(temp_pdf.name)
            markdown_content = result.document.export_to_markdown()
            
            # Upload original PDF to GCS
            bucket = storage_client.bucket(bucket_name)
            pdf_blob = bucket.blob(f"pdfs/{doc_id}.pdf")
            pdf_blob.upload_from_string(content, content_type="application/pdf")
            
            # Upload markdown to GCS
            md_blob = bucket.blob(f"markdown/{doc_id}.md")
            md_blob.upload_from_string(markdown_content, content_type="text/markdown")
            
            # Clean up temporary file
            os.unlink(temp_pdf.name)
            
            return {
                "message": "Document processed successfully",
                "document_id": doc_id,
                "pdf_url": pdf_blob.public_url,
                "markdown_url": md_blob.public_url
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint for monitoring
    """
    return {"status": "healthy"}

@app.get("/documents/", response_model=List[DocumentInfo])
async def list_documents(
    limit: int = Query(default=50, le=100, gt=0),
    prefix: str = Query(default="", description="Filter documents by prefix")
):
    """
    List all processed documents in the system
    """
    try:
        bucket = storage_client.bucket(bucket_name)
        
        # Get all PDF files from the bucket
        pdf_blobs = list(bucket.list_blobs(prefix=f"pdfs/{prefix}", max_results=limit))
        
        documents = []
        for pdf_blob in pdf_blobs:
            # Extract document ID from the PDF filename
            doc_id = pdf_blob.name.split('/')[-1].replace('.pdf', '')
            
            # Look up corresponding markdown file
            md_blob = bucket.blob(f"markdown/{doc_id}.md")
            
            if md_blob.exists():
                documents.append(
                    DocumentInfo(
                        document_id=doc_id,
                        pdf_url=pdf_blob.public_url,
                        markdown_url=md_blob.public_url,
                        created_at=pdf_blob.time_created.isoformat(),
                        size_bytes=pdf_blob.size
                    )
                )
        
        # Sort documents by creation date, newest first
        documents.sort(key=lambda x: x.created_at, reverse=True)
        
        return documents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add this at the bottom of the file
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 