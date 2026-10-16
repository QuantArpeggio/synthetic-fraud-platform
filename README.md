# Synthetic Financial Fraud Platform

An enterprise-grade synthetic transaction generator and automated fraud benchmark engine built with FastAPI, Pandas, and NumPy.

## 🚀 Features

- **Realistic Transaction Generation:** Configurable transaction streams with customizable baseline velocity, amount distributions, and geographical coordinates.
- **Targeted Anomaly Injection:** Inject key fraud patterns including **Geo-Impossibility** (impossible speed/distance travel) and **Benford's Law distribution anomalies** (first-digit fraud signals).
- **Automated Audit Reports:** Generates self-contained HTML benchmark reports containing statistical validation tests.

## ⚡ Live API & Interactive Docs

- **Swagger UI:** [https://synthetic-fraud-platform.onrender.com/docs](https://synthetic-fraud-platform.onrender.com/docs)

## 🛠️ Quickstart (Local)

1. **Clone repository:**
   ```bash
   git clone https://github.com/QuantArpeggio/synthetic-fraud-platform.git
   cd synthetic-fraud-platform
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run API locally:**
   ```bash
   uvicorn main:app --reload
   ```
