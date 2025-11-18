# 📦 **E-Commerce Order Processing Pipeline**

A lightweight data engineering pipeline that simulates an e-commerce order ingestion system using **LocalStack (SQS)**, **Redis**, **FastAPI**, and a background **SQS consumer**.

---

# 🚀 **Architecture**

```
Client → SQS Queue → Worker → Redis → FastAPI (Stats API)
```

### **Components**
- **SQS (LocalStack)** — receives incoming order events  
- **Worker** — validates orders, recalculates `order_value`, updates aggregates  
- **Redis** — stores global + per-user metrics  
- **FastAPI** — exposes analytics APIs  
- **Scripts** — utility scripts to send test events  

---

# 📂 **Project Structure**

```
E-commerce_pipeline/
├── docker-compose.yml
├── web/
│   ├── main.py
│   ├── api.py
│   ├── redis_client.py
│   └── Dockerfile
├── worker/
│   ├── consumer.py
│   ├── sqs_services.py
│   ├── redis_services.py
│   └── processing.py
├── scripts/
│   ├── send_order.py
│   ├── bulk_order.py
│   └── populate_sqs.py
└── README.md
```

---

# 🛠 **How It Works**

## **1️⃣ Queue is created & orders arrive in SQS**
(via `scripts/send_order.py` and `scripts/bulk_order.py`)

Each message contains:

- `order_id`
- `user_id`
- `order_timestamp`
- `items` → `{ quantity, price_per_unit }`

---

## **2️⃣ Worker consumes & validates messages**

### Worker Responsibilities:
- Validates all required fields  
- **Recalculates** `order_value = sum(qty × price_per_unit)`  
- Logs mismatch if original value is wrong  
- Updates **user-level stats**:
  - `order_count`
  - `total_spend`
- Updates **global stats**:
  - `total_orders`
  - `total_revenue`

---

## **3️⃣ FastAPI exposes analytics**

### **Available Endpoints**

| Endpoint | Description |
|----------|-------------|
| **`/health`** | Health check |
| **`/metrics`** | Global system stats |
| **`/users/{id}/stats`** | Stats for a single user |
| **`/stats/global`** | Global aggregates |
| **`/stats/top/{n}`** | Top N users by spend |
| **`/stats/monthly?start=YYYY-MM&end=YYYY-MM`** | Monthly range analytics |

---

# ▶️ **Running Locally**

## **1. Clone the repository**
```bash
git clone https://github.com/jayanthharwalkar/E-commerce_pipeline
cd E-commerce_pipeline
```

---

## **2. Start all services**
```bash
docker-compose up --build
```

This starts:
- LocalStack (SQS)
- Redis
- Worker
- FastAPI

---

## **3. Send sample orders**

### Send one order:
```bash
python scripts/send_order.py
```

### Send bulk orders:
```bash
python scripts/bulk_order.py 50
```

---

## **4. Test API endpoints**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
curl http://localhost:8000/users/{user_id}/stats
curl http://localhost:8000/stats/global
curl http://localhost:8000/stats/top/5
curl "http://localhost:8000/stats/monthly?start=2024-01&end=2024-12"
```

---

