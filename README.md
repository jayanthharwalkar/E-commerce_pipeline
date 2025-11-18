📦 E-Commerce Order Processing Pipeline

A lightweight data engineering pipeline that simulates an e-commerce order ingestion system using LocalStack (SQS), Redis, FastAPI, and a background SQS consumer.

🚀 Architecture
Client → SQS Queue → Worker → Redis → FastAPI (stats API)

Components

SQS (LocalStack) — queue for incoming orders

Worker — validates orders and updates aggregates

Redis — stores user + global metrics

FastAPI — exposes analytics endpoints

Scripts — populate SQS with sample order events

📂 Project Structure


<img width="598" height="510" alt="image" src="https://github.com/user-attachments/assets/b4f18242-d649-447e-a80d-5461cfd96332" />

🛠 How It Works
1. Queue is created and orders arrive in SQS (via scripts/send.py and scipts/bulk_send.py)

Each message includes:

order_id

user_id

timestamp

items (quantity, price_per_unit)

2. Worker consumes messages

Validates required fields

Recalculates order_value (items * price) and logs mismatches

Updates Redis user stats:

order_count

total_spend

Updates global stats:

total_orders

total_revenue

3. FastAPI exposes stats

/health
/metrics	
/users/{id}/stats	
/stats/global	
/stats/top/{n}
/stats/monthly

▶️ Running Locally
1. Clone repository
git clone https://github.com/jayanthharwalkar/E-commerce_pipeline
cd E-commerce_pipeline

2. Start services
docker-compose up --build

3. Send sample orders
python scripts/send_order.py
python scripts/bulk_order.py {number of sample orders}

5. Test API
curl http://localhost:8000/health <br>
curl http://localhost:8000/metrics <br>
curl http://localhost:8000/users/{user_id}/stats <br>
curl http://localhost:8000/stats/global <br>
curl http://localhost:8000/stats/top/5 <br>
curl "http://localhost:8000/stats/monthly?start={yyyy-mm}&end={yyyy-mm}" <br>






