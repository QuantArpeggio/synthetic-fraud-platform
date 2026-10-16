import math
import numpy as np
from scipy.stats import chisquare
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Any, Optional
from datetime import datetime

class TransactionSchema(BaseModel):
    transaction_id: str
    user_id: str
    timestamp: datetime
    amount: float = Field(gt=0.0)
    currency: str = Field(min_length=3, max_length=3)
    device_ip: str
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    is_fraud: Optional[bool] = False

class DatasetValidator:
    @staticmethod
    def validate_schema(raw_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        valid_records = []
        errors = []
        for idx, record in enumerate(raw_records):
            try:
                validated = TransactionSchema(**record)
                valid_records.append(validated.model_dump())
            except ValidationError as e:
                errors.append({"index": idx, "error": e.errors()})
        return {
            "total_checked": len(raw_records),
            "passed": len(valid_records),
            "failed": len(errors),
            "errors": errors,
            "clean_data": valid_records
        }

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @classmethod
    def validate_geo_velocity(cls, records: List[Dict[str, Any]], max_speed_kmh: float = 900.0) -> List[Dict[str, Any]]:
        user_transactions: Dict[str, List] = {}
        for rec in records:
            user_transactions.setdefault(rec["user_id"], []).append(rec)
            
        violations = []
        for user_id, txs in user_transactions.items():
            sorted_txs = sorted(txs, key=lambda x: x["timestamp"])
            for i in range(1, len(sorted_txs)):
                prev = sorted_txs[i - 1]
                curr = sorted_txs[i]
                dist_km = cls._haversine_distance(prev["latitude"], prev["longitude"], curr["latitude"], curr["longitude"])
                time_diff_hours = (curr["timestamp"] - prev["timestamp"]).total_seconds() / 3600.0
                if time_diff_hours <= 0:
                    continue
                speed = dist_km / time_diff_hours
                if speed > max_speed_kmh:
                    violations.append({
                        "user_id": user_id,
                        "transaction_id_1": prev["transaction_id"],
                        "transaction_id_2": curr["transaction_id"],
                        "distance_km": round(dist_km, 2),
                        "time_diff_hours": round(time_diff_hours, 2),
                        "calculated_speed_kmh": round(speed, 2),
                        "threshold_kmh": max_speed_kmh
                    })
        return violations

    @staticmethod
    def validate_benfords_law(records: List[Dict[str, Any]], p_value_threshold: float = 0.05) -> Dict[str, Any]:
        leading_digits = []
        for rec in records:
            amt_str = str(abs(rec["amount"])).replace(".", "").lstrip("0")
            if amt_str:
                digit = int(amt_str[0])
                if 1 <= digit <= 9:
                    leading_digits.append(digit)
                    
        if len(leading_digits) < 50:
            return {"status": "insufficient_data", "message": "Need at least 50 records for reliable Benford analysis."}
            
        observed = np.bincount(leading_digits)[1:]
        benford_probs = [math.log10(1 + 1/d) for d in range(1, 10)]
        expected = np.array(benford_probs) * len(leading_digits)
        chi2_stat, p_value = chisquare(f_obs=observed, f_exp=expected)
        passes = p_value >= p_value_threshold
        
        return {
            "passes_benford": passes,
            "chi2_statistic": round(chi2_stat, 4),
            "p_value": round(p_value, 4),
            "message": "Dataset matches Benford's Law natural distribution." if passes else "Warning: Dataset deviates significantly from Benford's Law."
        }
