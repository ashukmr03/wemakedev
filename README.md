# CareCircle API — Mobile-First Eldercare Coordination Backend

CareCircle is a FastAPI backend for eldercare coordination, enabling families to record care updates, extract structured information using Amazon Bedrock, manage tasks, track appointments, and view daily summaries.

## Quick Start (Local Run)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Run FastAPI Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Swagger UI will be available at: http://localhost:8000/docs

---

## Deploying to Render (Without Docker)

1. Create a **New Web Service** on Render connected to your repository.
2. Select **Python 3** environment.
3. Set **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
4. Set **Start Command**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Add Environment Variables in Render Dashboard:
   - `S3_BUCKET`: `carecircle-data`
   - `AWS_REGION`: `us-east-1`
   - `AWS_ACCESS_KEY_ID`: `<your-aws-access-key-id>`
   - `AWS_SECRET_ACCESS_KEY`: `<your-aws-secret-access-key>`
   - `BEDROCK_MODEL_ID`: `amazon.nova-lite-v1:0` (or `us.amazon.nova-lite-v1:0` in US regions)
   - `FRONTEND_URL`: `https://your-vercel-app.vercel.app`

---

## AWS Setup Checklist

1. **Amazon S3**:
   - Create private S3 bucket named `carecircle-data` (or update `S3_BUCKET` in env).
2. **Amazon Bedrock**:
   - Enable model access for `Amazon Nova Lite` in AWS Console (Bedrock -> Model access).
3. **AWS IAM Credentials**:
   - Ensure IAM user/role has permissions for `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`, `s3:DeleteObject`, and `bedrock:InvokeModel`/`bedrock:Converse`.

---

## Core API Contract

- `GET /health` -> Uptime & health status
- `GET /api/system/status` -> S3 & Bedrock status
- `GET /api/dashboard` -> Single-request full dashboard payload
- `POST /api/ai/extract` -> Bedrock structured care update extraction
- `POST /api/care/confirm` -> Human confirmation & entity creation
- `GET /api/care/timeline` -> Reverse-chronological care timeline
- `GET /api/tasks` -> List tasks
- `PATCH /api/tasks/{taskId}/complete` -> Complete task
- `POST /api/ai/summary` -> Generate AI daily summary
