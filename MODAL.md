# ⚡ Modal GPU Deployment (BACKUP - Free Tier)

**Keep as backup** - Free GPU deployment with excellent performance when warm, but 40-90s cold starts exceed Clerk JWT 60s expiry.

## Why Keep Modal as Backup?

- ✅ **Zero cost** - Free tier (30 GPU hours/month)
- ✅ **GPU speed** - 2-5s when warm (vs 500ms-2s CPU)
- ✅ **Already deployed** - No reason to tear down
- ✅ **Future-proof** - Can enable `keep_warm=1` when budget allows
- ✅ **Fallback** - If Railway has issues

## The JWT Problem

```
❌ PROBLEM:
User Query → Clerk JWT (60s expiry) → Modal Embedding Request
                ↓
        Modal GPU Cold Start: 40-90s ⚠️
                ↓
        JWT Expires → Auth Failure 💥

✅ SOLUTION: Use Railway (see RAILWAY.md)
```

## When to Use Modal

**Don't use for production** (use Railway instead)

**Good for:**
- Development/testing (free tier)
- Batch processing (non-JWT workloads)
- Future GPU tasks (image embeddings, fine-tuning)
- When budget allows `keep_warm=1` (~$20-30/month)

## Deploy to Modal

### 1. Install Modal

```bash
pip install modal
```

### 2. Authenticate

```bash
modal token new
```

### 3. Deploy

```bash
# In inception01 repo
modal deploy modal_inception.py
```

### 4. Get Your Modal URL

```bash
modal app list
# Example: https://verdict01--inception-verdict-web.modal.run
```

## Test Your Modal Deployment

```bash
# Health check
curl https://verdict01--inception-verdict-web.modal.run/health

# Generate embedding (expect 40-90s on cold start!)
time curl -X POST https://verdict01--inception-verdict-web.modal.run/ \
  -H "Content-Type: application/json" \
  -d '{"text": "landlord heating repair"}'

# Expected response:
# {
#   "embedding": [...768 numbers...],
#   "dimensions": 768,
#   "model": "modernbert-embed-base_finetune_512",
#   "latency_ms": 27605,  ⚠️ 27 seconds!
#   "device": "cuda:0"
# }
```

## Performance Characteristics

- **Cold start (first request):** 40-90s ⚠️
- **Warm requests:** 2-5s ✅
- **Idle timeout:** 120s (then cold again)
- **Free tier limit:** 30 GPU hours/month

## Enable Always-On (Optional - $20-30/month)

Edit `modal_inception.py`:

```python
@app.function(
    gpu="T4",
    keep_warm=1,  # Keep 1 GPU always warm ← ADD THIS
    timeout=60,
)
```

**Cost:** ~$20-30/month for always-on GPU

**Why this solves JWT issue:**
- No cold starts → 2-5s response time
- 2-5s << 60s JWT expiry ✅

## Cost Comparison

| Deployment | Cost/Month | Cold Start | JWT Safe? |
|------------|-----------|------------|-----------|
| Modal Free | $0 | 40-90s ❌ | ❌ No |
| Modal keep_warm | $20-30 | None ✅ | ✅ Yes |
| Railway CPU | $5-10 | None ✅ | ✅ Yes |

**Verdict:** Railway is more cost-effective for production

## Monitoring

```bash
# View logs
modal app logs inception-verdict

# Check usage
modal profile current
```

## Free Tier Limits

- **30 GPU hours/month** (then charges apply)
- Monitor usage: `modal profile current`
- Resets monthly

## Future Use Cases

**When budget allows keep_warm:**
- Faster than Railway CPU (2-5s vs 500ms-2s)
- Worth it when processing >10k embeddings/day

**Other GPU tasks:**
- Image embeddings (multimodal search)
- Model fine-tuning
- Batch processing

## Fallback Strategy

Keep Modal deployed as backup:

1. Primary: Railway (always-on CPU)
2. Fallback: Modal (if Railway down)
3. Future: Modal keep_warm (when scale justifies GPU cost)

```typescript
// embedding-service.ts fallback pattern
const ENDPOINTS = [
  process.env.INCEPTION_API_URL,        // Railway (primary)
  'https://verdict01--inception-verdict-web.modal.run', // Modal (backup)
];

async embedQuery(query: string) {
  for (const endpoint of ENDPOINTS) {
    try {
      return await this.tryEndpoint(endpoint, query);
    } catch (error) {
      console.warn(`Endpoint ${endpoint} failed, trying next...`);
    }
  }
  throw new Error('All embedding endpoints failed');
}
```

## Migration to Railway

**Don't delete Modal** - keep as backup:

1. Deploy Railway (see RAILWAY.md)
2. Update `INCEPTION_API_URL` to Railway
3. Keep Modal deployed (costs $0)
4. Add fallback logic (optional)

## Troubleshooting

### Cold Starts Too Long

- Expected behavior for free tier
- Use Railway instead for production
- Or enable `keep_warm=1` (~$20-30/month)

### GPU Out of Memory

```python
# Reduce batch size in modal_inception.py
model.encode(text, batch_size=1)  # Default: 32
```

### Free Tier Exhausted

```bash
# Check usage
modal profile current

# Options:
# 1. Wait for monthly reset
# 2. Add payment method
# 3. Use Railway instead
```

## Support

- Modal Docs: https://modal.com/docs
- Modal Discord: https://discord.gg/modal
- Inception Issues: https://github.com/verdict01/inception01/issues

---

**Status: ✅ Deployed as Backup (Free Tier)**  
**Production Use: ❌ Use Railway instead (see RAILWAY.md)**
