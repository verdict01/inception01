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

# Docker image: FreeLawProject Inception v2
# Contains ModernBERT model and FastAPI service
image = modal.Image.from_registry(
    "freelawproject/inception:v2",
).pip_install(
    "requests",  # For internal HTTP calls
)

# GPU configuration
# T4: Free tier (30 hrs/month), ~50ms inference
# A10G: Paid upgrade, ~30ms inference (if needed later)
GPU_CONFIG = modal.gpu.T4()

# Keep container warm for 2 minutes after last request
# Balances cold start avoidance with cost
SCALEDOWN_WINDOW = 120


@app.function(
    image=image,
    gpu=GPU_CONFIG,
    timeout=300,
    scaledown_window=SCALEDOWN_WINDOW,  # Updated from container_idle_timeout
    concurrency_limit=10,  # Updated from allow_concurrent_inputs
)
@modal.web_endpoint(method="POST")
async def embed_query(data: dict):
    """
    Generate 768-dim ModernBERT embedding for search query
    
    Request:
      POST /embed-query
      {"text": "landlord heating repair obligations"}
    
    Response:
      {
        "embedding": [0.123, -0.456, ..., 0.789],  // 768 floats
        "model": "modernbert-embed-base_finetune_512",
        "dimensions": 768
      }
    """
    import requests
    import time
    
    start_time = time.time()
    
    # Validate input
    if not data or "text" not in data:
        return {"error": "Missing 'text' field in request body"}, 400
    
    text = data["text"]
    if not text or not text.strip():
        return {"error": "Text cannot be empty"}, 400
    
    try:
        # Forward to Inception service running inside container on port 8005
        response = requests.post(
            "http://localhost:8005/api/v1/embed/query",
            json={"text": text},
            timeout=30
        )
        
        if not response.ok:
            return {
                "error": f"Inception API error: {response.status_code}",
                "details": response.text
            }, response.status_code
        
        result = response.json()
        
        # Validate embedding dimensions
        if "embedding" not in result:
            return {"error": "Invalid response from Inception"}, 500
        
        if len(result["embedding"]) != 768:
            return {
                "error": f"Invalid dimensions: expected 768, got {len(result['embedding'])}"
            }, 500
        
        # Add metadata
        result["latency_ms"] = int((time.time() - start_time) * 1000)
        result["dimensions"] = len(result["embedding"])
        result["model"] = "modernbert-embed-base_finetune_512"
        
        return result
        
    except requests.Timeout:
        return {"error": "Embedding generation timeout (30s)"}, 504
    except Exception as e:
        return {"error": f"Internal error: {str(e)}"}, 500


@app.function(
    image=image,
    gpu=GPU_CONFIG,
    scaledown_window=SCALEDOWN_WINDOW,
)
@modal.web_endpoint(method="GET")
async def health():
    """
    Health check endpoint
    
    Returns:
      {"status": "healthy", "service": "inception", "gpu": true}
    """
    import requests
    
    try:
        response = requests.get(
            "http://localhost:8005/health",
            timeout=5
        )
        
        return {
            "status": "healthy" if response.ok else "unhealthy",
            "service": "inception",
            "gpu": True,
            "inception_status": response.status_code
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "inception",
            "gpu": True,
            "error": str(e)
        }, 503


@app.function(
    image=image,
    gpu=GPU_CONFIG,
    scaledown_window=SCALEDOWN_WINDOW,
)
@modal.web_endpoint(method="GET")
async def info():
    """
    Get model and service information
    
    Returns:
      {
        "model": "modernbert-embed-base_finetune_512",
        "dimensions": 768,
        "max_tokens": 8192,
        "provider": "FreeLawProject",
        "gpu": "T4"
      }
    """
    import requests
    
    try:
        # Try to get info from Inception
        response = requests.get(
            "http://localhost:8005/",
            timeout=5
        )
        
        inception_info = response.json() if response.ok else {}
    except:
        inception_info = {}
    
    return {
        "model": "modernbert-embed-base_finetune_512",
        "dimensions": 768,
        "max_tokens": 8192,
        "provider": "FreeLawProject",
        "gpu": "T4",
        "deployment": "Modal",
        "version": "V5.10.0",
        "inception_info": inception_info
    }


# Local testing (optional)
if __name__ == "__main__":
    print("Deploy with: modal deploy modal_inception.py")
    print("Test locally with: modal serve modal_inception.py")
