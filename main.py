from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from generator import SyntheticTransactionEngine
from validator import DatasetValidator

app = FastAPI(
    title="Enterprise Synthetic Fraud Data API",
    description="On-demand generation and validation of financial transaction streams embedded with complex fraud matrices.",
    version="1.0.0"
)

class GenerationRequest(BaseModel):
    num_users: int = Field(default=30, ge=5, le=500, description="Number of synthetic user profiles to simulate")
    records_per_user: int = Field(default=15, ge=5, le=100, description="Baseline transactions generated per user")

class ValidationRequest(BaseModel):
    transactions: List[Dict[str, Any]] = Field(..., description="Raw list of transaction records to validate")
    max_speed_kmh: float = Field(default=900.0, description="Maximum physically plausible travel speed in km/h")

@app.get("/", summary="Health Check")
def health_check():
    return {"status": "online", "service": "Synthetic Data Platform API", "tier": "Enterprise MVP"}

@app.post("/api/v1/generate", summary="Generate Synthetic Financial Stream & Inject Fraud")
def generate_synthetic_stream(payload: GenerationRequest):
    """
    Generates baseline log-normal spending distributions and injects 
    Velocity Attacks, Structuring/Smurfing, and Geo-Impossibility matrices.
    """
    try:
        engine = SyntheticTransactionEngine(num_users=payload.num_users)
        # Note: If you want to customize records_per_user dynamically, 
        # you can pass it directly into generate_baseline_transactions inside generator.py
        data = engine.generate_full_dataset()
        
        fraud_count = sum(1 for tx in data if tx["is_fraud"])
        
        return {
            "status": "success",
            "metadata": {
                "total_records": len(data),
                "legitimate_records": len(data) - fraud_count,
                "injected_fraud_records": fraud_count
            },
            "transactions": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/api/v1/validate", summary="Run Comprehensive Quality & Compliance Validation Layer")
def validate_synthetic_stream(payload: ValidationRequest):
    """
    Runs schema checks, Haversine geo-velocity verification, and Benford's Law statistical profiling.
    """
    try:
        # 1. Schema Validation
        schema_results = DatasetValidator.validate_schema(payload.transactions)
        clean_data = schema_results["clean_data"]

        # 2. Geo-Velocity Violations Check
        velocity_violations = DatasetValidator.validate_geo_velocity(clean_data, max_speed_kmh=payload.max_speed_kmh)

        # 3. Benford's Law Statistical Check
        benford_results = DatasetValidator.validate_benfords_law(clean_data)

        return {
            "status": "success",
            "validation_report": {
                "schema_check": {
                    "total_checked": schema_results["total_checked"],
                    "passed": schema_results["passed"],
                    "failed": schema_results["failed"],
                    "error_logs": schema_results["errors"]
                },
                "geo_velocity_check": {
                    "violations_found": len(velocity_violations),
                    "details": velocity_violations
                },
                "benfords_law_check": benford_results
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
