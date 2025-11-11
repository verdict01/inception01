"""V5.10 Railway Deployment - Inception (ModernBERT) Embedding Service

Always-on CPU deployment for JWT-safe embedding generation.
Solves Modal GPU cold start issue (40-90s) exceeding Clerk JWT 60s expiry.

Model: freelawproject/modernbert-embed-base_finetune_512
Output: 768-dimensional embeddings
Hardware: Railway CPU (always-on, no cold starts)
Performance: ~500ms-2s (well under 60s JWT expiry)

Endpoints:
  POST /  - Generate embedding for search query
  GET  /health - Health check
  GET  /info - Model information
"""

import os
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer
import torch
import uvicorn

# Initialize FastAPI
app = FastAPI(
    title="Inception Verdict - ModernBERT Embeddings",
    version="V5.10.1",
    description="Always-on CPU deployment for JWT-safe embeddings"
)

# Load model at startup (cached in Docker image)
print("🚀 Loading ModernBERT model...")
model = SentenceTransformer(
    "freelawproject/modernbert-embed-base_finetune_512",
    device="cpu"  # Railway CPU deployment
)
print(f"✅ Model loaded on: {model.device}")


@app.post("/")
async def embed_query(request: Request):
    """
    Generate 768-dim ModernBERT embedding
    
    Request:
      POST /
      {"text": "landlord heating repair obligations"}
    
    Response:
      {
        "embedding": [0.123, -0.456, ..., 0.789],
        "dimensions": 768,
        "model": "modernbert-embed-base_finetune_512",
        "latency_ms": 1500,
        "device": "cpu"
      }
    """
    try:
        start_time = time.time()
        data = await request.json()
        
        if not data or "text" not in data:
            raise HTTPException(status_code=400, detail="Missing 'text' field")
        
        text = data["text"]
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Prefix for optimal results (from Inception)
        prefixed_text = f"search_query: {text}"
        
        # Generate embedding
        embedding = model.encode(
            prefixed_text,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        
        # Validate dimensions
        if len(embedding) != 768:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid dimensions: expected 768, got {len(embedding)}"
            )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        return {
            "embedding": embedding.tolist(),
            "dimensions": 768,
            "model": "modernbert-embed-base_finetune_512",
            "latency_ms": latency_ms,
            "device": str(model.device),
            "deployment": "Railway CPU (always-on)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check for Railway"""
    return {
        "status": "healthy",
        "model": "modernbert-embed-base_finetune_512",
        "device": str(model.device),
        "deployment": "Railway CPU",
        "always_on": True
    }


@app.get("/info")
async def info():
    """Model and deployment information"""
    return {
        "model": "modernbert-embed-base_finetune_512",
        "dimensions": 768,
        "max_tokens": 8192,
        "provider": "FreeLawProject",
        "hardware": "Railway CPU",
        "deployment": "Always-on (no cold starts)",
        "version": "V5.10.1",
        "jwt_safe": True,
        "typical_latency": "500ms-2s",
        "clerk_jwt_expiry": "60s (compatible)"
    }


@app.get("/")
async def root():
    """Root endpoint - returns service info"""
    return await info()


if __name__ == "__main__":
    # Get port from Railway environment variable (default 8000)
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting Inception Verdict on port {port}")
    print(f"📊 Model: ModernBERT (768 dims)")
    print(f"💻 Device: CPU (always-on)")
    print(f"⚡ Expected latency: 500ms-2s")
    print(f"🔐 JWT-safe: ✅ (well under 60s Clerk expiry)")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
