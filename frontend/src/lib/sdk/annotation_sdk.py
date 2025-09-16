"""
Annotation App Python SDK
Provides a Python interface for interacting with the Annotation API
"""

import json
import time
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlencode
import requests


@dataclass
class APIConfig:
    """Configuration for the API client"""
    api_key: str
    base_url: str = "https://api.annotation-app.com"
    timeout: int = 30
    retries: int = 3


@dataclass
class APIResponse:
    """Response wrapper for API calls"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


@dataclass
class Document:
    """Document model"""
    id: str
    title: str
    content: str
    created_at: str
    updated_at: str
    annotation_count: int
    status: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Annotation:
    """Annotation model"""
    id: str
    document_id: str
    start: int
    end: int
    text: str
    label: str
    confidence: Optional[float] = None
    annotator_id: Optional[str] = None
    created_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ExportOptions:
    """Export configuration options"""
    format: str  # json, conll, csv, standoff
    include_metadata: bool = True
    include_statistics: bool = True
    filter_labels: Optional[List[str]] = None
    encoding_scheme: str = "BIO"  # BIO, BILOU, IO
    csv_separator: str = ","


@dataclass
class ExportJob:
    """Export job status"""
    id: str
    status: str  # pending, processing, completed, failed
    document_id: str
    format: str
    created_at: str
    completed_at: Optional[str] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    progress: Optional[int] = None


@dataclass
class PaginatedResponse:
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    page: int
    pages: int
    limit: int


class HTTPClient:
    """HTTP client for making API requests"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """Make an HTTP request with error handling and retries"""
        url = urljoin(self.config.base_url, endpoint)
        
        for attempt in range(self.config.retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.config.timeout,
                    **kwargs
                )
                
                # Handle JSON response
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = response.text
                
                if response.ok:
                    return APIResponse(success=True, data=data)
                else:
                    error_msg = data.get("error", f"HTTP {response.status_code}: {response.reason}") if isinstance(data, dict) else str(data)
                    return APIResponse(success=False, error=error_msg)
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.config.retries - 1:  # Last attempt
                    return APIResponse(success=False, error=str(e))
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return APIResponse(success=False, error="Max retries exceeded")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> APIResponse:
        """Make a GET request"""
        return self._request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> APIResponse:
        """Make a POST request"""
        json_data = data if data is not None else {}
        return self._request("POST", endpoint, json=json_data)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> APIResponse:
        """Make a PUT request"""
        json_data = data if data is not None else {}
        return self._request("PUT", endpoint, json=json_data)
    
    def delete(self, endpoint: str) -> APIResponse:
        """Make a DELETE request"""
        return self._request("DELETE", endpoint)


class DocumentsAPI:
    """Documents API client"""
    
    def __init__(self, client: HTTPClient):
        self.client = client
    
    def list(self, page: int = 1, limit: int = 20, search: Optional[str] = None, 
             sort_by: Optional[str] = None, sort_order: str = "desc") -> APIResponse:
        """List all documents"""
        params = {
            "page": page,
            "limit": limit,
            "sort_order": sort_order,
        }
        if search:
            params["search"] = search
        if sort_by:
            params["sort_by"] = sort_by
            
        return self.client.get("/api/documents", params)
    
    def get(self, document_id: str) -> APIResponse:
        """Get a specific document by ID"""
        return self.client.get(f"/api/documents/{document_id}")
    
    def create(self, document: Dict[str, Any]) -> APIResponse:
        """Create a new document"""
        return self.client.post("/api/documents", document)
    
    def update(self, document_id: str, updates: Dict[str, Any]) -> APIResponse:
        """Update an existing document"""
        return self.client.put(f"/api/documents/{document_id}", updates)
    
    def delete(self, document_id: str) -> APIResponse:
        """Delete a document"""
        return self.client.delete(f"/api/documents/{document_id}")
    
    def export(self, document_id: str, options: ExportOptions) -> APIResponse:
        """Export document annotations"""
        export_data = asdict(options)
        return self.client.post(f"/api/documents/{document_id}/export", export_data)
    
    def get_export_job(self, job_id: str) -> APIResponse:
        """Get export job status"""
        return self.client.get(f"/api/export-jobs/{job_id}")
    
    def download_export(self, job_id: str) -> APIResponse:
        """Download export file"""
        try:
            url = urljoin(self.client.config.base_url, f"/api/export-jobs/{job_id}/download")
            response = self.client.session.get(url, stream=True)
            
            if response.ok:
                return APIResponse(success=True, data=response.content)
            else:
                return APIResponse(success=False, error=f"HTTP {response.status_code}: {response.reason}")
                
        except requests.exceptions.RequestException as e:
            return APIResponse(success=False, error=str(e))


class AnnotationsAPI:
    """Annotations API client"""
    
    def __init__(self, client: HTTPClient):
        self.client = client
    
    def list(self, document_id: str, page: int = 1, limit: int = 100, 
             label: Optional[str] = None) -> APIResponse:
        """List annotations for a document"""
        params = {
            "page": page,
            "limit": limit,
        }
        if label:
            params["label"] = label
            
        return self.client.get(f"/api/documents/{document_id}/annotations", params)
    
    def get(self, annotation_id: str) -> APIResponse:
        """Get a specific annotation"""
        return self.client.get(f"/api/annotations/{annotation_id}")
    
    def create(self, annotation: Dict[str, Any]) -> APIResponse:
        """Create a new annotation"""
        return self.client.post("/api/annotations", annotation)
    
    def update(self, annotation_id: str, updates: Dict[str, Any]) -> APIResponse:
        """Update an existing annotation"""
        return self.client.put(f"/api/annotations/{annotation_id}", updates)
    
    def delete(self, annotation_id: str) -> APIResponse:
        """Delete an annotation"""
        return self.client.delete(f"/api/annotations/{annotation_id}")
    
    def bulk_create(self, annotations: List[Dict[str, Any]]) -> APIResponse:
        """Bulk create annotations"""
        return self.client.post("/api/annotations/bulk", {"annotations": annotations})


class AnnotationAPI:
    """Main SDK client"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.annotation-app.com"):
        """Initialize the API client"""
        config = APIConfig(api_key=api_key, base_url=base_url)
        self.client = HTTPClient(config)
        self.documents = DocumentsAPI(self.client)
        self.annotations = AnnotationsAPI(self.client)
    
    def ping(self) -> APIResponse:
        """Test API connection"""
        return self.client.get("/api/ping")
    
    def status(self) -> APIResponse:
        """Get API status and version"""
        return self.client.get("/api/status")


class AnnotationUtils:
    """Utility functions for working with annotations"""
    
    @staticmethod
    def calculate_stats(annotations: List[Annotation]) -> Dict[str, Any]:
        """Calculate annotation statistics"""
        if not annotations:
            return {
                "total": 0,
                "labels": {},
                "annotators": {},
                "average_length": 0,
                "total_length": 0,
            }
        
        label_counts = {}
        annotator_counts = {}
        total_length = 0
        
        for annotation in annotations:
            # Count labels
            label_counts[annotation.label] = label_counts.get(annotation.label, 0) + 1
            
            # Count annotators
            if annotation.annotator_id:
                annotator_counts[annotation.annotator_id] = annotator_counts.get(annotation.annotator_id, 0) + 1
            
            # Calculate text length
            total_length += len(annotation.text)
        
        return {
            "total": len(annotations),
            "labels": label_counts,
            "annotators": annotator_counts,
            "average_length": total_length / len(annotations),
            "total_length": total_length,
        }
    
    @staticmethod
    def find_overlaps(annotations: List[Annotation]) -> List[Dict[str, Any]]:
        """Find overlapping annotations"""
        overlaps = []
        
        for i, ann1 in enumerate(annotations):
            for ann2 in annotations[i + 1:]:
                # Check if they're for the same document
                if ann1.document_id != ann2.document_id:
                    continue
                
                # Check for overlap
                overlap_start = max(ann1.start, ann2.start)
                overlap_end = min(ann1.end, ann2.end)
                
                if overlap_start < overlap_end:
                    overlaps.append({
                        "annotation1": ann1,
                        "annotation2": ann2,
                        "overlap_start": overlap_start,
                        "overlap_end": overlap_end,
                    })
        
        return overlaps
    
    @staticmethod
    def to_conll(text: str, annotations: List[Annotation], scheme: str = "BIO") -> str:
        """Convert annotations to CoNLL format"""
        tokens = text.split()
        token_annotations = ["O"] * len(tokens)
        
        current_pos = 0
        for i, token in enumerate(tokens):
            token_start = text.find(token, current_pos)
            token_end = token_start + len(token)
            
            # Find annotations that cover this token
            for annotation in annotations:
                if annotation.start <= token_start and annotation.end >= token_end:
                    is_first = i == 0 or not token_annotations[i - 1].endswith(annotation.label)
                    
                    if scheme == "BIO":
                        token_annotations[i] = f"{'B' if is_first else 'I'}-{annotation.label}"
                    elif scheme == "IO":
                        token_annotations[i] = f"I-{annotation.label}"
                    elif scheme == "BILOU":
                        # Find if this is the last token of the annotation
                        is_last = i == len(tokens) - 1 or not any(
                            a.label == annotation.label and 
                            a.start <= text.find(tokens[i + 1], token_end) and 
                            a.end >= text.find(tokens[i + 1], token_end) + len(tokens[i + 1])
                            for a in annotations
                        )
                        
                        if is_first and is_last:
                            token_annotations[i] = f"U-{annotation.label}"
                        elif is_first:
                            token_annotations[i] = f"B-{annotation.label}"
                        elif is_last:
                            token_annotations[i] = f"L-{annotation.label}"
                        else:
                            token_annotations[i] = f"I-{annotation.label}"
                    break  # Use first matching annotation
            
            current_pos = token_end
        
        # Build CoNLL output
        lines = []
        for token, annotation in zip(tokens, token_annotations):
            lines.append(f"{token}\t{annotation}")
        
        return "\n".join(lines)
    
    @staticmethod
    def from_conll(conll_text: str) -> List[Dict[str, Any]]:
        """Parse CoNLL format to annotations"""
        annotations = []
        lines = conll_text.strip().split("\n")
        tokens = []
        labels = []
        
        for line in lines:
            if line.strip():
                parts = line.split("\t")
                if len(parts) >= 2:
                    tokens.append(parts[0])
                    labels.append(parts[1])
        
        # Convert token-level labels to span annotations
        current_annotation = None
        text_pos = 0
        
        for i, (token, label) in enumerate(zip(tokens, labels)):
            if label != "O":
                prefix, label_name = label.split("-", 1) if "-" in label else ("I", label)
                
                if prefix in ["B", "U"] or current_annotation is None or current_annotation["label"] != label_name:
                    # Start new annotation
                    if current_annotation:
                        annotations.append(current_annotation)
                    
                    current_annotation = {
                        "start": text_pos,
                        "end": text_pos + len(token),
                        "text": token,
                        "label": label_name,
                    }
                else:
                    # Continue current annotation
                    current_annotation["end"] = text_pos + len(token)
                    current_annotation["text"] += " " + token
                
                if prefix in ["L", "U"]:
                    # End current annotation
                    annotations.append(current_annotation)
                    current_annotation = None
            else:
                # No annotation for this token
                if current_annotation:
                    annotations.append(current_annotation)
                    current_annotation = None
            
            text_pos += len(token) + 1  # +1 for space
        
        # Add final annotation if exists
        if current_annotation:
            annotations.append(current_annotation)
        
        return annotations


# Example usage
if __name__ == "__main__":
    # Initialize the client
    client = AnnotationAPI(api_key="your_api_key_here")
    
    # Test connection
    ping_result = client.ping()
    print(f"Ping result: {ping_result}")
    
    # List documents
    docs_result = client.documents.list(limit=10)
    if docs_result.success:
        print(f"Found {len(docs_result.data['items'])} documents")
    else:
        print(f"Error: {docs_result.error}")
    
    # Create a document
    new_doc = {
        "title": "Test Document",
        "content": "This is a test document for annotation.",
        "metadata": {"source": "api_test"}
    }
    
    create_result = client.documents.create(new_doc)
    if create_result.success:
        doc_id = create_result.data["id"]
        print(f"Created document with ID: {doc_id}")
        
        # Create an annotation
        annotation = {
            "document_id": doc_id,
            "start": 10,
            "end": 14,
            "text": "test",
            "label": "KEYWORD"
        }
        
        ann_result = client.annotations.create(annotation)
        if ann_result.success:
            print(f"Created annotation: {ann_result.data}")
        else:
            print(f"Error creating annotation: {ann_result.error}")
    else:
        print(f"Error creating document: {create_result.error}")
