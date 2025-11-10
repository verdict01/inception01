"""V5.10 Modal Deployment - Inception (ModernBERT) Embedding Service

Deploys FreeLawProject's Inception microservice to Modal with GPU support.
Generates 768-dimensional legal embeddings for Verdict semantic search.

Model: freelawproject/modernbert-embed-base_finetune_512
Output: 768-dimensional embeddings (despite "512" in name)
GPU: T4 (free tier: 30 hours/month)

Usage:
  modal deploy modal_inception.py

Endpoints:
  POST /embed-query  - Generate embedding for search query
  GET  /health       - Health check
  GET  /info         - Model info
"""

import modal

# Create Modal app
app = modal.App("inception-verdict")

# Build from Inception source (since Docker Hub image not accessible)
# This will clone the repo and build from Dockerfile
image = (
    modal.Image.from_dockerfile(
        "https://github.com/freelawproject/inception.git",
        dockerfile_path="Dockerfile",
        context_mount=modal.Mount.from_local_dir(
            ".",
            remote_path="/root/context",
            condition=lambda pth: False,  # Don't mount anything
        ),
        build_args={"TARGET_ENV": "prod"},
    )
)

# GPU configuration - updated to Modal 1.0 syntax
GPU_CONFIG = "T4"  # Changed from modal.gpu.T4()

# Keep container warm for 2 minutes after last request
SCALEDOWN_WINDOW = 120


@app.function(
    image=image,
    gpu=GPU_CONFIG,
    timeout=300,
    scaledown_window=SCALEDOWN_WINDOW,
    max_containers=10,  # Updated from concurrency_limit
)
@modal.asgi_app()
def embed_query_endpoint():
    """
    Main FastAPI endpoint - forwards to Inception service
    
    This mounts the Inception FastAPI app running on port 8005
    """
    import subprocess
    import time
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse
    import requests
    
    # Start Inception service in background
    subprocess.Popen([
        "uvicorn",
        "inception.main:app",
        "--host", "0.0.0.0",
        "--port", "8005",
        "--workers", "1",
    ])
    
    # Wait for service to start
    time.sleep(5)
    
    # Create FastAPI wrapper
    web_app = FastAPI(title="Inception Verdict Wrapper")
    
    @web_app.post("/embed-query")
    async def embed_query(request: Request):
        """Generate 768-dim ModernBERT embedding"""
        try:
            data = await request.json()
            
            if not data or "text" not in data:
                raise HTTPException(status_code=400, detail="Missing 'text' field")
            
            # Forward to Inception
            response = requests.post(
                "http://localhost:8005/api/v1/embed/query",
                json={"text": data["text"]},
                timeout=30
            )
            
            if not response.ok:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Inception error: {response.text}"
                )
            
            result = response.json()
            
            # Validate
            if "embedding" not in result or len(result["embedding"]) != 768:
                raise HTTPException(
                    status_code=500,
                    detail=f"Invalid embedding: {len(result.get('embedding', []))} dimensions"
                )
            
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @web_app.get("/health")
    async def health():
        """Health check"""
        try:
            response = requests.get("http://localhost:8005/health", timeout=5)
            return {
                "status": "healthy" if response.ok else "unhealthy",
                "inception_status": response.status_code
            }
        except:
            return {"status": "unhealthy"}
    
    @web_app.get("/info")
    async def info():
        """Model info"""
        return {
            "model": "modernbert-embed-base_finetune_512",
            "dimensions": 768,
            "max_tokens": 8192,
            "provider": "FreeLawProject",
            "gpu": "T4",
            "deployment": "Modal",
            "version": "V5.10.0"
        }
    
    return web_app


if __name__ == "__main__":
    print("Deploy with: modal deploy modal_inception.py")
    print("This will build from https://github.com/freelawproject/inception")
