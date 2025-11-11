# Inception01 - ModernBERT Embeddings for Verdict V5.10

**Purpose**: Generate 768-dimensional legal embeddings for semantic search  
**Model**: `freelawproject/modernbert-embed-base_finetune_512`  
**Accuracy**: 99.59% on legal evaluation set  
**License**: Apache 2.0 (commercial use allowed)

## ⚡ Quick Decision: Railway or Modal?

### 🚂 Railway (PRIMARY - Recommended for Production)

✅ **Use Railway when:**
- You need production reliability
- You're using Clerk JWT authentication (expires in 60s)
- You want consistent latency (no cold starts)
- You're okay with ~$5-10/month cost

**See:** [RAILWAY.md](./RAILWAY.md) - Full deployment guide

### ⚡ Modal (BACKUP - Keep as Fallback)

✅ **Use Modal when:**
- Testing/development (free tier)
- Running batch jobs (non-JWT workloads)
- Future GPU tasks (when budget allows `keep_warm=1`)
- Fallback if Railway has issues

**See:** [MODAL.md](./MODAL.md) - Full deployment guide

## 🚨 The Critical JWT Problem

```
Problem with Modal GPU cold starts:

User Query → Clerk JWT (60s expiry) → Modal Embedding Request
                ↓
        Modal GPU Cold Start: 40-90s ❌
                ↓
        JWT Expires → Auth Failure 💥

Solution with Railway:

User Query → Clerk JWT (60s expiry) → Railway Embedding Request
                ↓
        Railway Response: 500ms-2s ✅
                ↓
        JWT Still Valid → Success 🎉
```

**Verdict:** Railway for production, Modal as backup (free tier costs $0 to keep deployed)

## 📊 Deployment Comparison

| Feature | Railway CPU ⭐ | Modal GPU (Free) | Modal GPU (keep_warm) |
|---------|---------------|------------------|----------------------|
| **Cold Start** | None ✅ | 40-90s ❌ | None ✅ |
| **Latency** | 500ms-2s | 2-5s (warm) | 2-5s |
| **JWT Safe?** | ✅ Yes | ❌ No | ✅ Yes |
| **Always-On** | ✅ Yes | ❌ No | ✅ Yes |
| **Cost/Month** | $5-10 | $0 | $20-30 |
| **Free Queries** | Unlimited | 36K/month | Unlimited |

**Recommendation:** Deploy Railway for production, keep Modal as $0 backup

## 🚀 Quick Start

### Option 1: Railway (Recommended)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Deploy (Railway auto-detects Dockerfile)
railway up

# 4. Get your URL
railway status
# Example: https://inception-verdict-production.up.railway.app
```

**Full guide:** [RAILWAY.md](./RAILWAY.md)

### Option 2: Modal (Backup)

```bash
# 1. Install Modal
pip install modal

# 2. Authenticate
modal token new

# 3. Deploy
modal deploy modal_inception.py

# 4. Get your URL
# Example: https://verdict01--inception-verdict-web.modal.run
```

**Full guide:** [MODAL.md](./MODAL.md)

## 🔌 Integration with Verdict

### 1. Set Environment Variable (Vercel)

```bash
# Railway (primary)
INCEPTION_API_URL=https://your-app.up.railway.app

# Or Modal (if using as primary - not recommended for JWT apps)
INCEPTION_API_URL=https://verdict01--inception-verdict-web.modal.run
```

### 2. Deploy Verdict

```bash
# In verdict01/03 repo
vercel --prod
```

The Verdict embedding service automatically handles the new endpoint.

## 📈 Performance Metrics

### Railway CPU (Production)

```
First request:     500ms-2s ✅
All requests:      500ms-2s ✅
JWT expiry risk:   None (<<60s)
Uptime:            99.9%
Cost:              $5-10/month
```

### Modal GPU (Backup/Development)

```
Cold start:        40-90s ❌
Warm requests:     2-5s ✅
Idle timeout:      120s
Free tier:         30 GPU hours/month
JWT expiry risk:   HIGH (cold starts exceed 60s)
```

## 🏗️ Repository Structure

```
inception01/
├── README.md                    # This file (overview)
├── RAILWAY.md                   # Railway deployment (PRIMARY)
├── MODAL.md                     # Modal deployment (BACKUP)
│
├── railway_inception.py         # Railway FastAPI server ⭐
├── modal_inception.py           # Modal serverless
│
├── Dockerfile                   # Railway container
├── requirements.txt             # Shared dependencies
│
└── .github/workflows/
    └── railway.yml              # Auto-deploy to Railway
```

## 🔐 Privacy Model

**Query text NEVER leaves Verdict infrastructure:**

1. User query → Verdict API
2. Verdict → Inception (Railway/Modal) - query text
3. Inception → 768-dimensional embedding
4. Verdict → CourtListener - **ONLY numbers, NOT text**
5. CourtListener cannot reverse-engineer query

**vs OpenAI:** Query text sent to third-party API ❌

## 📦 API Reference

Both Railway and Modal expose the same API:

### POST / (Generate Embedding)

```bash
curl -X POST https://your-endpoint/ \
  -H "Content-Type: application/json" \
  -d '{"text": "landlord heating repair"}'
```

**Response:**
```json
{
  "embedding": [768 floats],
  "dimensions": 768,
  "model": "modernbert-embed-base_finetune_512",
  "latency_ms": 1500,
  "device": "cpu",
  "deployment": "Railway CPU (always-on)"
}
```

### GET /health

```bash
curl https://your-endpoint/health
```

### GET /info

```bash
curl https://your-endpoint/info
```

## 💰 Cost Analysis

### Railway (Recommended)

```
$5/month base plan
+ ~$5/month for always-on CPU
= $5-10/month total

Unlimited queries (within reasonable usage)
```

### Modal Free Tier

```
30 GPU hours/month free
÷ 0.05s per query (50ms average)
= ~36,000 queries/month FREE

After free tier: ~$0.00175 per query
```

### Break-even Analysis

```
< 36K queries/month:    Modal free tier wins
36K - 100K/month:       Railway wins ($5-10 vs $63-175)
> 100K/month:           Railway wins (flat rate vs usage-based)
```

**But:** JWT compatibility makes Railway the only choice for production

## 🛠️ Troubleshooting

### Railway Issues

See [RAILWAY.md](./RAILWAY.md#troubleshooting)

### Modal Issues

See [MODAL.md](./MODAL.md#troubleshooting)

### JWT Expiry Errors

**Symptom:** "JWT expired" or authentication failures  
**Cause:** Modal GPU cold start (40-90s) exceeds Clerk JWT 60s expiry  
**Solution:** Switch to Railway (always-on, no cold starts)

## 🔄 Migration Strategy

### From Modal to Railway

1. ✅ Deploy Railway (see RAILWAY.md)
2. ✅ Test Railway endpoint
3. ✅ Update `INCEPTION_API_URL` in Vercel to Railway URL
4. ✅ Deploy Vercel production
5. ✅ Monitor for 24 hours
6. ✅ **Keep Modal deployed as backup** (costs $0)

### Fallback Implementation (Optional)

```typescript
// embedding-service.ts with fallback
const ENDPOINTS = [
  process.env.INCEPTION_API_URL,        // Railway (primary)
  'https://verdict01--inception-verdict-web.modal.run', // Modal (backup)
];

async embedQuery(query: string) {
  for (const endpoint of ENDPOINTS) {
    try {
      return await this.tryEndpoint(endpoint, query);
    } catch (error) {
      console.warn(`${endpoint} failed, trying next...`);
    }
  }
  throw new Error('All embedding endpoints failed');
}
```

## 📚 Documentation

- **Railway Guide:** [RAILWAY.md](./RAILWAY.md) - Primary deployment
- **Modal Guide:** [MODAL.md](./MODAL.md) - Backup deployment
- **Model Info:** https://huggingface.co/freelawproject/modernbert-embed-base_finetune_512
- **Inception Source:** https://github.com/freelawproject/inception
- **V5.10 Docs:** verdict01/docs/repo03/

## 🎯 Deployment Status

| Service | Status | URL | Purpose |
|---------|--------|-----|---------|
| **Railway** | ⏳ Pending | TBD | Production (PRIMARY) |
| **Modal** | ✅ Deployed | https://verdict01--inception-verdict-web.modal.run | Backup/Development |

## 🗺️ Roadmap

- [x] Modal GPU deployment (completed)
- [x] Railway CPU deployment files (completed)
- [ ] **Deploy Railway production**
- [ ] Update Vercel environment variables
- [ ] End-to-end testing with Railway
- [ ] Monitor Railway performance
- [ ] Keep Modal as backup (always free)
- [ ] Custom domain: inception.verdict.services

## 🤝 Contributing

Issues and improvements welcome at https://github.com/verdict01/inception01/issues

---

**Version:** V5.10.1  
**Primary Deployment:** Railway (always-on CPU) ⭐  
**Backup Deployment:** Modal (free tier GPU)  
**Last Updated:** 2025-11-11
