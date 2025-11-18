📦 E-Commerce Order Processing Pipeline

A lightweight data engineering pipeline that simulates an end-to-end e-commerce order ingestion and analytics system using LocalStack (SQS), Redis, FastAPI, and a background SQS consumer.

🚀 Architecture
Client → SQS Queue → Worker → Redis → FastAPI (Analytics API)

Components

SQS (LocalStack) — queue for incoming order events

Worker — validates orders, fixes order_value mismatches, updates aggregates

Redis — stores user-level & global metrics

FastAPI — exposes analytics endpoints

Scripts — generate and send sample orders

📂 Project Structure
E-commerce_pipeline/
├── docker-compose.yml
├── web/                  # FastAPI application
│   ├── main.py
│   ├── api.py
│   ├── redis_client.py
│   └── Dockerfile
├── worker/               # SQS-consuming worker
│   ├── consumer.py
│   ├── sqs_services.py
│   ├── redis_services.py
│   └── processing.py
├── scripts/
│   ├── send_order.py
│   ├── bulk_order.py
│   └── populate_sqs.py
└── README.md

🛠 How It Works
1️⃣ Queue is created and orders arrive in SQS

(via scripts/send_order.py and scripts/bulk_order.py)

Each incoming message contains:

order_id

user_id

order_timestamp

items (quantity, price_per_unit)

2️⃣ Worker consumes and validates messages

The worker performs:

✔ Validates required fields

✔ Recalculates order_value = sum(quantity × price_per_unit)

✔ Logs mismatch if provided order_value is wrong

✔ Updates user-level stats in Redis:

order_count

total_spend

✔ Updates global stats:

total_orders

total_revenue

3️⃣ FastAPI exposes analytics

Available endpoints:

Endpoint	Description
/health	Service health check
/metrics	Global system metrics
/users/{id}/stats	Stats for a single user
/stats/global	Global aggregated metrics
/stats/top/{n}	Top N users by spend
/stats/monthly?start=YYYY-MM&end=YYYY-MM	Monthly range stats
▶️ Running Locally
1. Clone repository
git clone https://github.com/jayanthharwalkar/E-commerce_pipeline
cd E-commerce_pipeline

2. Start services
docker-compose up --build


This starts:

LocalStack (SQS)

Redis

Worker service

FastAPI server

3. Send sample orders
python scripts/send_order.py
python scripts/bulk_order.py 50        # example: send 50 random orders

4. Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/metrics
curl http://localhost:8000/users/{user_id}/stats
curl http://localhost:8000/stats/global
curl http://localhost:8000/stats/top/5
curl "http://localhost:8000/stats/monthly?start=2024-01&end=2024-12"
