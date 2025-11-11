"""V5.10.2 Railway Deployment - Inception (ModernBERT) Embedding Service

Always-on CPU deployment for JWT-safe embedding generation.
Solves Modal GPU cold start issue (40-90s) exceeding Clerk JWT 60s expiry.

Model: freelawproject/modernbert-embed-base_finetune_512
Output: 768-dimensional embeddings
Hardware: Railway CPU (always-on, no cold starts)
Performance: ~500ms-2s (well under 60s JWT expiry)

V5.10.2 Optimizations:
- CPU threading optimizations (set_num_threads, set_num_interop_threads)
- Inference mode (model.eval())
- Normalized embeddings for consistency
- Batch size 1 for CPU efficiency

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

# =====================================================
# CPU OPTIMIZATIONS (V5.10.2)
# =====================================================
print("⚡ Configuring CPU optimizations...")

# Railway Free: 2 vCPU, 1 GB RAM
# Optimal thread count: 4 (2x vCPU count)
torch.set_num_threads(4)
torch.set_num_interop_threads(2)

# Disable gradient computation (inference only)
torch.set_grad_enabled(False)

print(f"✅ CPU threads: {torch.get_num_threads()}")
print(f"✅ Interop threads: {torch.get_num_interop_threads()}")

# Initialize FastAPI
app = FastAPI(
    title="Inception Verdict - ModernBERT Embeddings",
    version="V5.10.2",
    description="Always-on CPU deployment with threading optimizations"
)

# =====================================================
# MODEL LOADING (V5.10.2)
# =====================================================
print("🚀 Loading ModernBERT model...")
model = SentenceTransformer(
    "freelawproject/modernbert-embed-base_finetune_512",
    device="cpu"  # Railway CPU deployment
)

# Set to evaluation mode (disables dropout, batch norm)
model.eval()

print(f"✅ Model loaded on: {model.device}")
print(f"✅ Evaluation mode: {not model.training}")


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
        
        # Generate embedding with CPU optimizations
        with torch.no_grad():  # Ensure no gradient tracking
            embedding = model.encode(
                prefixed_text,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True,  # L2 normalization for consistency
                batch_size=1  # Single query, no batching overhead
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
            "deployment": "Railway CPU (V5.10.2 optimized)"
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
        "version": "V5.10.2",
        "optimizations": {
            "cpu_threads": torch.get_num_threads(),
            "interop_threads": torch.get_num_interop_threads(),
            "eval_mode": not model.training
        },
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
        "hardware": "Railway CPU (2 vCPU, 1 GB)",
        "deployment": "Always-on (no cold starts)",
        "version": "V5.10.2",
        "optimizations": [
            "CPU threading (4 threads)",
            "Interop parallelism (2 threads)",
            "Inference mode (eval)",
            "Normalized embeddings",
            "No gradient tracking"
        ],
        "jwt_safe": True,
        "typical_latency": "500ms-2s (target)",
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
    print(f"⚡ CPU threads: {torch.get_num_threads()}")
    print(f"⚡ Interop threads: {torch.get_num_interop_threads()}")
    print(f"⚡ Expected latency: 500ms-2s")
    print(f"🔐 JWT-safe: ✅ (well under 60s Clerk expiry)")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
