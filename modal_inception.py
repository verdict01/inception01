"""V5.10 Modal Deployment - Inception (ModernBERT) Embedding Service

Deploys FreeLawProject's Inception microservice to Modal with GPU support.
Generates 768-dimensional legal embeddings for Verdict semantic search.

Model: freelawproject/modernbert-embed-base_finetune_512
Output: 768-dimensional embeddings (despite "512" in name)
GPU: T4 (free tier: 30 hours/month)

Usage:
  modal deploy modal_inception.py

Endpoints:
  POST /  - Generate embedding for search query
  GET  /health - Health check
"""

import modal

# Create Modal app
app = modal.App("inception-verdict")

# Build image with Inception dependencies
# This installs from GitHub and downloads ModernBERT model
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "sentence-transformers>=3.0.0",
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.32.0",
        "pydantic>=2.9.0",
        "pydantic-settings>=2.5.0",
        "prometheus-client>=0.21.0",
        "nltk>=3.9.0",
        "torch>=2.5.0",
        "transformers>=4.46.0",
    )
    .run_commands(
        "python -c 'import nltk; nltk.download(\"punkt_tab\")'",
        "python -c 'from sentence_transformers import SentenceTransformer; SentenceTransformer(\"freelawproject/modernbert-embed-base_finetune_512\")'",
    )
)

# GPU configuration
GPU_CONFIG = "T4"
SCALEDOWN_WINDOW = 120


@app.function(
    image=image,
    gpu=GPU_CONFIG,
    timeout=300,
    scaledown_window=SCALEDOWN_WINDOW,
    max_containers=10,
)
@app.asgi_app()
def web():
    """
    FastAPI app for ModernBERT embeddings
    """
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse
    from sentence_transformers import SentenceTransformer
    import torch
    
    # Load model once at startup
    print("Loading ModernBERT model...")
    model = SentenceTransformer(
        "freelawproject/modernbert-embed-base_finetune_512",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    print(f"Model loaded on: {model.device}")
    
    # Create FastAPI app
    web_app = FastAPI(
        title="Inception Verdict - ModernBERT Embeddings",
        version="V5.10.0"
    )
    
    @web_app.post("/")
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
            "model": "modernbert-embed-base_finetune_512"
          }
        """
        import time
        
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
                "device": str(model.device)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @web_app.get("/health")
    async def health():
        """Health check"""
        return {
            "status": "healthy",
            "model": "modernbert-embed-base_finetune_512",
            "device": str(model.device),
            "gpu_available": torch.cuda.is_available()
        }
    
    @web_app.get("/info")
    async def info():
        """Model info"""
        return {
            "model": "modernbert-embed-base_finetune_512",
            "dimensions": 768,
            "max_tokens": 8192,
            "provider": "FreeLawProject",
            "gpu": "T4" if torch.cuda.is_available() else "CPU",
            "deployment": "Modal",
            "version": "V5.10.0"
        }
    
    return web_app


if __name__ == "__main__":
    print("Deploy with: modal deploy modal_inception.py")
    print("This will install ModernBERT and run on Modal GPU")
