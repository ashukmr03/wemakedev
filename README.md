<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=230&color=gradient&customColorList=12,20,24&text=CareCircle%20AI&fontSize=64&fontColor=FFF6EE&fontAlignY=38&animation=fadeIn&desc=Mobile-first%20eldercare%20coordination%20backend&descSize=20&descAlignY=60&descColor=C9D8E2" alt="CareCircle AI" width="100%"/>

<a href="https://github.com/ashukmr03/wemakedev">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3000&pause=900&color=FF7A8A&center=true&vCenter=true&width=720&height=50&lines=Record+a+care+update+in+plain+words;AI+turns+it+into+tasks+and+appointments;Family+confirms%2C+everyone+stays+in+the+loop;Daily+summaries%2C+one+request+away" alt="Typing animation" />
</a>

<br/>

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Amazon Bedrock](https://img.shields.io/badge/Amazon%20Bedrock-Nova%20Lite-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![Amazon S3](https://img.shields.io/badge/Amazon%20S3-569A31?style=for-the-badge&logo=amazons3&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)

<br/>

[![Live Demo](https://img.shields.io/badge/Live%20Demo-care--circle--three--psi.vercel.app-FF7A8A?style=for-the-badge&logo=vercel&logoColor=white)](https://care-circle-three-psi.vercel.app)
![Stars](https://img.shields.io/github/stars/ashukmr03/wemakedev?style=for-the-badge&color=FFC86B)
![Last Commit](https://img.shields.io/github/last-commit/ashukmr03/wemakedev?style=for-the-badge&color=7FD6C2)

</div>

---

## ✨ About

**CareCircle** is a FastAPI backend for eldercare coordination. Families can:

- 📝 **Record** care updates in everyday language
- 🤖 **Extract** structured information using **Amazon Bedrock**
- ✅ **Manage tasks** and track **appointments**
- 📅 **View** a reverse-chronological care timeline
- 🧾 **Get** AI-generated daily summaries

---

## 🔄 How It Works

```mermaid
flowchart LR
    A[👨‍👩‍👧 Family member<br/>records update] --> B[🤖 Bedrock<br/>extracts tasks & appointments]
    B --> C{🙋 Human<br/>confirmation}
    C -->|Confirm| D[(🪣 S3<br/>care data)]
    D --> E[📋 Tasks]
    D --> F[🗓️ Timeline]
    D --> G[🧾 Daily summary]
```

---

## 🚀 Quick Start (Local Run)

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### 3️⃣ Run FastAPI Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

📖 Swagger UI will be available at: <http://localhost:8000/docs>

---

## 🌐 Deploying to Render (Without Docker)

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

   | Variable | Value |
   | --- | --- |
   | `S3_BUCKET` | `carecircle-data` |
   | `AWS_REGION` | `us-east-1` |
   | `AWS_ACCESS_KEY_ID` | `<your-aws-access-key-id>` |
   | `AWS_SECRET_ACCESS_KEY` | `<your-aws-secret-access-key>` |
   | `BEDROCK_MODEL_ID` | `amazon.nova-lite-v1:0` (or `us.amazon.nova-lite-v1:0` in US regions) |
   | `FRONTEND_URL` | `https://your-vercel-app.vercel.app` |

---

## ☁️ AWS Setup Checklist

- [ ] **Amazon S3**: create a private bucket named `carecircle-data` (or update `S3_BUCKET` in env).
- [ ] **Amazon Bedrock**: enable model access for `Amazon Nova Lite` (Bedrock → Model access).
- [ ] **AWS IAM**: allow `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`, `s3:DeleteObject`, and `bedrock:InvokeModel` / `bedrock:Converse`.

---

## 📡 Core API Contract

| Method | Endpoint | Description |
| :---: | --- | --- |
| `GET` | `/health` | Uptime & health status |
| `GET` | `/api/system/status` | S3 & Bedrock status |
| `GET` | `/api/dashboard` | Single-request full dashboard payload |
| `POST` | `/api/ai/extract` | Bedrock structured care update extraction |
| `POST` | `/api/care/confirm` | Human confirmation & entity creation |
| `GET` | `/api/care/timeline` | Reverse-chronological care timeline |
| `GET` | `/api/tasks` | List tasks |
| `PATCH` | `/api/tasks/{taskId}/complete` | Complete task |
| `POST` | `/api/ai/summary` | Generate AI daily summary |

---

<div align="center">

Made with ❤️ for the people who care for the people we love.

<img src="https://capsule-render.vercel.app/api?type=waving&height=110&color=gradient&customColorList=12,20,24&section=footer" width="100%" alt="footer"/>

</div>
