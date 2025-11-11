# 🚂 Railway Deployment (PRIMARY - Production Ready)

**✅ DEPLOYED:** https://inception01-production.up.railway.app

**Recommended for production** - Always-on CPU deployment that solves Modal GPU cold start + Clerk JWT timing issues.

## 🎉 V5.10.2 Performance Breakthrough!

**Before (V5.10.1):** 22,000ms (22 seconds) ❌  
**After (V5.10.2):** **108ms** (0.1 seconds) ✅  
**Improvement:** **200x faster!**

## Why Railway?

| Feature | Railway CPU V5.10.2 | Modal GPU | Winner |
|---------|---------------------|-----------|--------|
| **Cold Start** | None ✅ | 40-90s ❌ | Railway |
| **Latency** | **~100ms ⚡** | 2-5s (warm) | **Railway** |
| **JWT Compatible** | ✅ Yes (<<60s) | ❌ No (>60s cold) | Railway |
| **Always-On** | ✅ Yes | ❌ No | Railway |
| **Cost/Month** | $5-10 | $0 (30h free) | Railway* |
| **Reliability** | ✅ High | ⚠️ Cold starts | Railway |

*Railway is faster and more reliable for production despite small cost

## The JWT Problem Railway Solves

```
User Query → Clerk JWT (60s expiry) → Embedding Request
                ↓
        Modal GPU Cold Start: 40-90s ❌
                ↓
        JWT Expires → Auth Failure 💥

Railway V5.10.2 Solution:
User Query → Clerk JWT (60s expiry) → Embedding Request
                ↓
        Railway Response: ~100ms ⚡
                ↓
        JWT Still Valid → Success 🎉
```

## ✅ Current Deployment

**Production URL:** https://inception01-production.up.railway.app  
**Version:** V5.10.2 (CPU Optimized)  
**Performance:** ~100ms per embedding (200x faster!)

**Test it:**
```bash
# Health check (see optimization stats)
curl https://inception01-production.up.railway.app/health

# Generate embedding (~100ms!)
curl -X POST https://inception01-production.up.railway.app/ \
  -H "Content-Type: application/json" \
  -d '{"text": "landlord heating repair"}'
```

## 🚀 V5.10.2 CPU Optimizations

What made the 200x improvement possible:

1. **Thread Optimization**
   - `torch.set_num_threads(4)` - Optimal for Railway 2 vCPU
   - `torch.set_num_interop_threads(2)` - Parallel operations

2. **Inference Mode**
   - `model.eval()` - Disables dropout/batch normalization
   - `torch.set_grad_enabled(False)` - No gradient computation
   - `with torch.no_grad()` - Context manager for safety

3. **Encoding Optimizations**
   - `normalize_embeddings=True` - L2 normalization
   - `batch_size=1` - No batching overhead for single queries

4. **Model Configuration**
   - Pre-loaded at startup (no lazy loading)
   - Cached in Docker image layer
   - Always-on service (no cold starts)

## Quick Deploy to Railway

### 1. Create Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project (or create new)
railway link
```

### 2. Deploy from GitHub

**Option A: Railway Dashboard (Recommended)**

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `verdict01/inception01`
5. Railway auto-detects Dockerfile ✅
6. Click "Deploy"

**Option B: CLI**

```bash
# In inception01 repo
railway up
```

### 3. Configure Environment Variables

Railway automatically sets `PORT` - no config needed!

### 4. Get Your Railway URL

```bash
railway status
# Example: https://inception01-production.up.railway.app
```

### 5. Update Vercel Environment Variable

```bash
INCEPTION_API_URL=https://inception01-production.up.railway.app
```

## Test Your Railway Deployment

```bash
# Health check (V5.10.2 includes optimization stats)
curl https://inception01-production.up.railway.app/health

# Expected response:
# {
#   "status": "healthy",
#   "model": "modernbert-embed-base_finetune_512",
#   "device": "cpu",
#   "deployment": "Railway CPU",
#   "version": "V5.10.2",
#   "optimizations": {
#     "cpu_threads": 4,
#     "interop_threads": 2,
#     "eval_mode": true
#   },
#   "always_on": true
# }

# Generate embedding (~100ms!)
time curl -X POST https://inception01-production.up.railway.app/ \
  -H "Content-Type: application/json" \
  -d '{"text": "landlord heating repair"}'

# Expected response (~100ms):
# {
#   "embedding": [...768 numbers...],
#   "dimensions": 768,
#   "model": "modernbert-embed-base_finetune_512",
#   "latency_ms": 108,
#   "device": "cpu",
#   "deployment": "Railway CPU (V5.10.2 optimized)"
# }
```

## Performance Expectations

**V5.10.2 Measured Performance:**
- **First request:** ~100ms (no cold start!)
- **All subsequent requests:** ~100ms (consistent)
- **JWT expiry window:** 60s (safe: 100ms << 60,000ms)
- **Uptime:** 99.9% (Railway SLA)
- **200x faster than V5.10.1!** 🚀

**V5.10.1 Performance (Before Optimization):**
- First request: ~22,000ms (22 seconds) ❌
- Cause: Unoptimized CPU inference without threading
- Fixed by: V5.10.2 CPU optimizations

## Cost Breakdown

**Railway Hobby Plan: $5/month**
- Includes: $5 usage credit
- CPU usage: ~$0.000463/minute
- Monthly cost for always-on: ~$5-10

**Comparison:**
- Railway always-on (V5.10.2): $5-10/month ✅ **BEST VALUE**
- Modal keep_warm GPU: $20-30/month 💰
- Modal free tier: $0 but cold starts ❌

## Scaling on Railway

**Vertical Scaling:**
```bash
# Increase memory if needed (current: 1 GB sufficient)
railway variables set RAILWAY_MEMORY=2048
```

**Horizontal Scaling:**
- Railway Pro: Multiple replicas with load balancing
- Cost: ~$20/month for 2 replicas
- **Not needed yet:** Single replica handles ~100ms latency

## Monitoring

**View Logs:**
```bash
railway logs
```

**Check for V5.10.2 startup logs:**
```
⚡ Configuring CPU optimizations...
✅ CPU threads: 4
✅ Interop threads: 2
🚀 Loading ModernBERT model...
✅ Model loaded on: cpu
✅ Evaluation mode: True
```

**Metrics:**
- Railway dashboard shows CPU, memory, requests/sec
- Built-in health checks (every 30s)
- V5.10.2: Monitor latency_ms in responses (~100ms expected)

## Troubleshooting

### V5.10.2: Still Seeing High Latency (>1s)

**Check version:**
```bash
curl https://inception01-production.up.railway.app/health | jq '.version'
# Should show: "V5.10.2"
```

**If not V5.10.2:**
1. Verify latest commit deployed: `railway status`
2. Force redeploy: `railway up --detach`
3. Check logs: `railway logs`

**Expected startup logs:**
```
✅ CPU threads: 4
✅ Interop threads: 2
✅ Evaluation mode: True
```

### Deployment Failed

```bash
# Check logs
railway logs

# Rebuild
railway up --detach
```

### Image Too Large (8.3GB)

**Solution:** Already fixed in latest Dockerfile
- Uses CPU-only PyTorch (~200MB vs ~2GB CUDA)
- Multi-stage build
- Final image: ~2.5GB (under 4GB limit)

### Memory Issues

```bash
# Increase memory allocation (default 1GB works fine)
railway variables set RAILWAY_MEMORY=2048
```

### V5.10.1 Performance Issue (Resolved in V5.10.2)

**Symptom:** 22s latency instead of expected 500ms-2s

**Root Cause:** CPU inference without thread optimization

**Solution:** Updated to V5.10.2 with:
- `torch.set_num_threads(4)`
- `torch.set_num_interop_threads(2)`
- `model.eval()`
- `torch.no_grad()`

**Result:** 200x faster (22s → 108ms)

## Rollback

```bash
# List deployments
railway deployments

# Rollback to previous (not recommended - V5.10.2 is best)
railway deployments rollback <deployment-id>
```

## CI/CD (Auto-Deploy)

Railway automatically deploys on git push to main:

1. Push to `inception01` main branch
2. Railway detects change
3. Builds new Docker image
4. Deploys with zero downtime ✅

**V5.10.2 deployed:** 2025-11-11 (200x performance improvement)

## Security

- Railway uses HTTPS by default ✅
- No API keys needed (stateless service)
- Model cached in Docker image
- No user data stored

## Migration from Modal

1. ✅ Deploy to Railway (DONE)
2. ✅ Test endpoint (DONE)
3. ✅ V5.10.2 Optimization (DONE - 200x faster!)
4. ✅ Update `INCEPTION_API_URL` in Vercel (READY)
5. ⏳ Deploy Vercel
6. ⏳ Monitor for 24 hours
7. ✅ Keep Modal as backup (free tier)

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Inception Issues: https://github.com/verdict01/inception01/issues

---

**Status: ✅ Deployed and Production Ready**  
**URL:** https://inception01-production.up.railway.app  
**Version:** V5.10.2 (CPU Optimized - 200x Faster!)  
**Performance:** ~100ms per embedding (measured)  
**Clerk JWT Safe:** ✅ (100ms << 60s expiry)
