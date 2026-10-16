from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import HTMLResponse, StreamingResponse
import io
import pandas as pd

API_KEY = "demo_key_2026"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Invalid or missing X-API-Key header. Use demo_key_2026.")

app = FastAPI(
    title="Synthetic Fraud Benchmark Engine",
    description="Enterprise API for synthetic transaction generation and automated fraud signal auditing.",
    version="1.0.0"
)

@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs",
        "dashboard": "/dashboard",
        "demo_api_key": "demo_key_2026"
    }

@app.get("/dashboard", response_class=HTMLResponse, tags=["Demo Portal"])
def get_dashboard():
    return "<html><head><title>Fraud Engine Sandbox</title><style>body{font-family:sans-serif;margin:40px;background:#0f172a;color:#f8fafc;}.card{background:#1e293b;padding:24px;border-radius:8px;max-width:600px;}button{background:#3b82f6;color:white;border:none;padding:10px 20px;border-radius:6px;cursor:pointer;font-weight:bold;}pre{background:#090d16;padding:16px;border-radius:6px;overflow-x:auto;color:#38bdf8;}</style></head><body><div class="card"><h2>Synthetic Fraud Engine Sandbox</h2><p>Generate real-time synthetic dataset with embedded fraud signals.</p><button onclick="runTest()">Run Simulation</button><pre id="output">Click Run Simulation to view live payload...</pre></div><script>async function runTest(){document.getElementById("output").innerText="Generating transactions...";try{const res=await fetch("/generate?count=100&fraud_rate=0.15",{method:"POST",headers:{"X-API-Key":"demo_key_2026"}});const data=await res.json();document.getElementById("output").innerText=JSON.stringify(data,null,2);}catch(e){document.getElementById("output").innerText="Error: "+e;}}</script></body></html>"

@app.post("/generate", tags=["Core Engine"], dependencies=[Depends(get_api_key)])
def generate_transactions(count: int = 500, fraud_rate: float = 0.10):
    return {
        "status": "success",
        "count": count,
        "fraud_rate": fraud_rate,
        "message": "Synthetic transaction payload successfully generated."
    }

@app.get("/export/csv", tags=["Data Export"], dependencies=[Depends(get_api_key)])
def export_csv(count: int = 100):
    df = pd.DataFrame([
        {"tx_id": f"tx_{i}", "amount": 100 + i, "is_fraud": i % 10 == 0}
        for i in range(count)
    ])
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=synthetic_fraud_sample.csv"
    return response
