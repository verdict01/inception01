# 🚂 Railway Deployment (PRIMARY - Production Ready)

**✅ DEPLOYED:** https://inception01-production.up.railway.app

**Recommended for production** - Always-on CPU deployment that solves Modal GPU cold start + Clerk JWT timing issues.

## Why Railway?

| Feature | Railway CPU | Modal GPU | Winner |
|---------|------------|-----------|--------|
| **Cold Start** | None ✅ | 40-90s ❌ | Railway |
| **Latency** | 500ms-2s ✅ | 2-5s (warm) | Railway* |
| **JWT Compatible** | ✅ Yes (<60s) | ❌ No (>60s cold) | Railway |
| **Always-On** | ✅ Yes | ❌ No | Railway |
| **Cost/Month** | $5-10 | $0 (30h free) | Modal |
| **Reliability** | ✅ High | ⚠️ Cold starts | Railway |

*Railway CPU is actually faster for production due to zero cold starts

## The JWT Problem Modal Solves

```
User Query → Clerk JWT (60s expiry) → Embedding Request
                ↓
        Modal GPU Cold Start: 40-90s ❌
                ↓
        JWT Expires → Auth Failure 💥

Railway Solution:
User Query → Clerk JWT (60s expiry) → Embedding Request
                ↓
        Railway Response: 500ms-2s ✅
                ↓
        JWT Still Valid → Success 🎉
```

## ✅ Current Deployment

**Production URL:** https://inception01-production.up.railway.app

**Test it:**
```bash
# Health check
curl https://inception01-production.up.railway.app/health

# Generate embedding (500ms-2s)
curl -X POST https://inception01-production.up.railway.app/ \
  -H "Content-Type: application/json" \
  -d '{"text": "landlord heating repair"}'
```

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
# Health check
curl https://inception01-production.up.railway.app/health

# Expected response:
# {
#   "status": "healthy",
#   "model": "modernbert-embed-base_finetune_512",
#   "device": "cpu",
#   "deployment": "Railway CPU",
#   "always_on": true
# }

# Generate embedding
curl -X POST https://inception01-production.up.railway.app/ \
  -H "Content-Type: application/json" \
  -d '{"text": "landlord heating repair"}'

# Expected response (500ms-2s):
# {
#   "embedding": [...768 numbers...],
#   "dimensions": 768,
#   "model": "modernbert-embed-base_finetune_512",
#   "latency_ms": 1500,
#   "device": "cpu",
#   "deployment": "Railway CPU (always-on)"
# }
```

## Performance Expectations

- **First request:** ~500ms-2s (no cold start!)
- **All subsequent requests:** ~500ms-2s (consistent)
- **JWT expiry window:** 60s (safe: 500ms-2s << 60s)
- **Uptime:** 99.9% (Railway SLA)

## Cost Breakdown

**Railway Hobby Plan: $5/month**
- Includes: $5 usage credit
- CPU usage: ~$0.000463/minute
- Monthly cost for always-on: ~$5-10

**Comparison:**
- Railway always-on: $5-10/month ✅
- Modal keep_warm GPU: $20-30/month 💰
- Modal free tier: $0 but cold starts ❌

## Scaling on Railway

**Vertical Scaling:**
```bash
# Increase memory if needed
railway variables set RAILWAY_MEMORY=2048
```

**Horizontal Scaling:**
- Railway Pro: Multiple replicas with load balancing
- Cost: ~$20/month for 2 replicas

## Monitoring

**View Logs:**
```bash
railway logs
```

**Metrics:**
- Railway dashboard shows CPU, memory, requests/sec
- Built-in health checks (every 30s)

## Troubleshooting

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

### High Latency (>5s)

- Check Railway metrics (CPU/memory)
- Consider upgrading plan
- Check if model is loaded (should load at startup)

### Memory Issues

```bash
# Increase memory allocation
railway variables set RAILWAY_MEMORY=4096
```

## Rollback

```bash
# List deployments
railway deployments

# Rollback to previous
railway deployments rollback <deployment-id>
```

## CI/CD (Auto-Deploy)

Railway automatically deploys on git push to main:

1. Push to `inception01` main branch
2. Railway detects change
3. Builds new Docker image
4. Deploys with zero downtime ✅

## Security

- Railway uses HTTPS by default ✅
- No API keys needed (stateless service)
- Model cached in Docker image
- No user data stored

## Migration from Modal

1. ✅ Deploy to Railway (DONE)
2. ✅ Test endpoint (DONE)
3. ⏳ Update `INCEPTION_API_URL` in Vercel
4. ⏳ Deploy Vercel
5. ⏳ Monitor for 24 hours
6. ✅ Keep Modal as backup (free tier)

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Inception Issues: https://github.com/verdict01/inception01/issues

---

**Status: ✅ Deployed and Production Ready**  
**URL:** https://inception01-production.up.railway.app  
**Version:** V5.10.1
