# Inception01 - ModernBERT Deployment for Verdict V5.10

Deployment configurations for FreeLawProject's Inception microservice (ModernBERT embeddings).

## Overview

**Purpose**: Generate 768-dimensional legal embeddings for semantic search  
**Model**: `freelawproject/modernbert-embed-base_finetune_512`  
**Accuracy**: 99.59% on legal evaluation set  
**License**: Apache 2.0 (commercial use allowed)  

## Deployment Options

### 1. Modal GPU (Recommended for Testing)

**Pros**:
- Free tier: 30 GPU hours/month (~36K queries)
- GPU acceleration: ~50ms latency
- Auto-scales to zero (no idle costs)
- 2-minute deployment

**Deploy**:
```bash
pip install modal
modal setup
modal deploy modal_inception.py
```

**Output**:
```
✓ Created endpoints:
  POST https://your-username--inception-verdict-embed-query.modal.run
  GET  https://your-username--inception-verdict-health.modal.run
  GET  https://your-username--inception-verdict-info.modal.run
```

**Test**:
```bash
curl -X POST https://your-username--inception-verdict-embed-query.modal.run \
  -H "Content-Type: application/json" \
  -d '{"text": "landlord heating repair obligations"}'
```

**Expected Response**:
```json
{
  "embedding": [0.123, -0.456, ..., 0.789],
  "dimensions": 768,
  "model": "modernbert-embed-base_finetune_512",
  "latency_ms": 52
}
```

### 2. Railway CPU (Alternative)

**Pros**:
- Free $5 credit/month
- Always-on reliability
- Custom domain support
- Simple deployment

**Cons**:
- CPU only: ~500ms latency
- Less cost-effective at scale

**Deploy**: (Coming soon)

## Integration with Verdict

### Environment Variables

Add to Vercel:
```bash
# Enable semantic search
ENABLE_SEMANTIC_SEARCH=true

# Modal GPU endpoint
INCEPTION_API_URL=https://your-username--inception-verdict.modal.run
```

### API Compatibility

The Modal deployment is compatible with Verdict's `embeddingService`:

```typescript
// src/lib/services/embedding-service.ts
const response = await fetch(`${this.baseUrl}/embed-query`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: query })
});
```

**Note**: Modal endpoint is `/embed-query` (not `/api/v1/embed/query`)  
This is already handled in the wrapper.

## Performance Expectations

### Modal GPU (T4)
```
Cold start:    2-3 seconds (first request after idle)
Warm latency:  50-100ms (GPU inference)
Concurrency:   10 simultaneous requests
Idle timeout:  2 minutes (keeps warm)
```

### Cache Behavior
```
Cache hit:     ~50-100ms (pgvector lookup + Modal)
Cache miss:    ~2-3s (Modal + CourtListener semantic search)
Hit rate:      95%+ (semantic clustering)
```

## Cost Analysis

### Modal Free Tier
```
30 GPU hours/month
÷ 0.05s per query
= 36,000 queries/month FREE
```

### Beyond Free Tier
```
Modal GPU: $0.000035/second
≈ $0.00175 per query (50ms)
≈ $20-30/month at 10K queries/month
```

### Break-even vs OpenAI
```
OpenAI: $0.0004 per query (1536-dim)
Modal:  $0.00175 per query (768-dim GPU)

Modal cheaper when:
- Using free tier (0-36K queries)
- High volume with CPU (>100K queries)

OpenAI cheaper when:
- 36K-200K queries/month (past free tier, before CPU)
```

## Testing Strategy

### Week 1: Modal GPU
```bash
# Deploy Modal
modal deploy modal_inception.py

# Update Vercel env
ENABLE_SEMANTIC_SEARCH=true
INCEPTION_API_URL=https://your-modal-url.modal.run

# Test queries
"landlord heating repair"
"tenant rights uninhabitable conditions"
"implied warranty of habitability"

# Monitor:
- Latency: Should be ~50-100ms
- Quality: Compare to keyword search
- GPU hours: Track usage in Modal dashboard
```

### Week 2: Railway CPU (Optional)
```bash
# Deploy Railway
railway up

# Update Vercel env
INCEPTION_API_URL=https://your-railway-app.railway.app

# Compare:
- Latency: ~500ms (acceptable?)
- Quality: Same model, same results
- Cost: $10/month CPU vs $0 Modal free tier
```

## Troubleshooting

### Modal Cold Starts
**Problem**: First request after 2 min idle takes 2-3s
**Solution**: Increase `container_idle_timeout` in `modal_inception.py`
```python
container_idle_timeout=300  # Keep warm 5 minutes
```

### Modal GPU Quota
**Problem**: "GPU quota exceeded"
**Solution**: Either:
1. Wait for monthly reset
2. Upgrade to paid plan
3. Switch to Railway CPU temporarily

### Invalid Dimensions
**Problem**: "Expected 768, got 512"
**Solution**: Model outputs 768 despite name - check Inception version

### Health Check Fails
**Problem**: `/health` returns 503
**Solution**: Container starting up (wait 10-30s after deploy)

## Monitoring

### Modal Dashboard
```
https://modal.com/apps/inception-verdict

Metrics:
- Request count
- GPU hours used
- Latency (p50, p95, p99)
- Error rate
```

### Verdict Logs
```
[Storage V5.10] Using ModernBERT embedding (semantic search enabled)
[EmbeddingService V5.10] Generating ModernBERT embedding
[EmbeddingService V5.10] ✅ Successfully generated 768-dim embedding
```

## Roadmap

- [x] Modal GPU deployment
- [ ] Railway CPU deployment (comparison)
- [ ] A/B testing infrastructure
- [ ] Custom domain (inception.verdict.services)
- [ ] Production deployment decision
- [ ] Monitoring dashboard

## Links

- **Inception**: https://github.com/freelawproject/inception
- **ModernBERT**: https://huggingface.co/freelawproject/modernbert-embed-base_finetune_512
- **Modal Docs**: https://modal.com/docs
- **V5.10 Reference**: verdict01/docs/repo03/AI-SDK-5-CASE-LAW-SYSTEM-V5.10-SEMANTIC-SEARCH-REFERENCE.md

---

**Version**: V5.10.0  
**Status**: Testing (Modal GPU)  
**Last Updated**: 2025-11-10
