mk# Productivity Analysis Microservice - Integration Guide

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [API Reference](#api-reference)
4. [Integration Examples](#integration-examples)
5. [Project Ideas](#project-ideas)
6. [Advanced Features](#advanced-features)
7. [Monitoring & Scaling](#monitoring--scaling)
8. [Troubleshooting](#troubleshooting)

## Overview

This document provides guidance on integrating the Productivity Analysis Microservice into various applications. The service offers productivity insights through a RESTful API built with FastAPI.

## Quick Start

### Prerequisites
- Node.js 16+ (for Express integration)
- Python 3.8+
- Docker (optional, for containerized deployment)

### Running the Service

1. Start the service:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Test the API:
   ```bash
   curl -X POST http://localhost:8000/api/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{"user_id":"123","tasks":[...],...}'
   ```

## API Reference

### POST /api/v1/analyze

**Request Body:**
```json
{
  "user_id": "string",
  "tasks": [
    {
      "id": "string",
      "title": "string",
      "planned_minutes": number,
      "actual_minutes": number,
      "completed": boolean
    }
  ],
  "deep_work_minutes": number,
  "meetings_minutes": number,
  "interruptions": number,
  "sleep_hours": number
}
```

**Response:**
```json
{
  "score": 72.5,
  "tags": ["string"],
  "insight": "string",
  "recommendations": ["string"],
  "key_points": ["string"]
}
```

## Integration Examples

### Express.js Integration

1. Install required packages:
   ```bash
   npm install axios express
   ```

2. Create a service layer (`services/analysis.service.js`):
   ```javascript
   const axios = require('axios');
   
   class AnalysisService {
     constructor(baseURL = 'http://localhost:8000') {
       this.client = axios.create({ baseURL });
     }
     
     async analyzeProductivity(userId, taskData) {
       const response = await this.client.post('/api/v1/analyze', {
         user_id: userId,
         ...taskData
       });
       return response.data;
     }
   }
   
   module.exports = new AnalysisService();
   ```

3. Create an API route (`routes/analysis.js`):
   ```javascript
   const express = require('express');
   const analysisService = require('../services/analysis.service');
   const router = express.Router();
   
   router.post('/analyze', async (req, res) => {
     try {
       const result = await analysisService.analyzeProductivity(
         req.user.id, 
         req.body
       );
       res.json(result);
     } catch (error) {
       res.status(500).json({ error: 'Analysis failed' });
     }
   });
   
   module.exports = router;
   ```

## Project Ideas

### 1. Team Productivity Dashboard
- Real-time team performance metrics
- Workload distribution analysis
- Meeting effectiveness scores

### 2. Personal Productivity Coach
- Daily/weekly productivity reports
- Habit tracking integration
- Personalized improvement recommendations

### 3. Smart Task Manager
- Automatic task prioritization
- Focus time optimization
- Distraction analysis

## Advanced Features

### Caching Strategy
Enable Redis caching for improved performance:

1. Start Redis:
   ```bash
   docker run -d -p 6379:6379 redis
   ```

2. Update `.env`:
   ```ini
   REDIS_HOST=localhost
   REDIS_PORT=6379
   CACHE_EXPIRE_SECONDS=3600
   ```

### Webhook Support
Configure webhooks for asynchronous processing:

```python
# Example webhook handler
@app.post("/webhooks/productivity")
async def handle_webhook(webhook: WebhookData):
    # Process in background
    asyncio.create_task(process_webhook(webhook))
    return {"status": "processing"}
```

## Monitoring & Scaling

### Health Check Endpoint
```
GET /health
```

### Prometheus Metrics
Enable metrics collection:
```python
from prometheus_client import start_http_server, Counter

REQUESTS = Counter('http_requests_total', 'Total HTTP requests')

@app.middleware("http")
async def count_requests(request: Request, call_next):
    REQUESTS.inc()
    return await call_next(request)
```

### Docker Compose
Example `docker-compose.yml`:
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Verify the service is running
   - Check port configuration
   - Ensure no firewall is blocking the connection

2. **Rate Limiting**
   - Check `RATE_LIMIT` setting
   - Implement exponential backoff in client code

3. **Redis Connection Issues**
   - Verify Redis is running
   - Check connection string and credentials
   - Monitor Redis memory usage

### Getting Help

For additional support:
- Check the project's GitHub issues
- Review API documentation at `/docs`
- Enable debug logging with `DEBUG=true`

---
*Documentation generated on December 16, 2025*
