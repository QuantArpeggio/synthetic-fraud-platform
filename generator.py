import random
import uuid
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

class SyntheticTransactionEngine:
    def __init__(self, num_users: int = 50, base_date: datetime = None):
        self.num_users = num_users
        self.base_date = base_date or datetime(2026, 6, 1, 9, 0, 0)
        
        self.users = [
            {
                "user_id": f"usr_{str(uuid.uuid4())[:8]}",
                "base_lat": round(random.uniform(25.0, 48.0), 4),
                "base_lon": round(random.uniform(-125.0, -70.0), 4),
                "device_ip": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
            }
            for _ in range(self.num_users)
        ]

    def generate_baseline_transactions(self, records_per_user: int = 10) -> List[Dict[str, Any]]:
        transactions = []
        mu = 3.5
        sigma = 0.8
        
        for user in self.users:
            current_time = self.base_date
            for _ in range(records_per_user):
                current_time += timedelta(hours=random.randint(1, 12))
                amount = round(float(np.random.lognormal(mean=mu, sigma=sigma)), 2)
                
                transactions.append({
                    "transaction_id": f"tx_{str(uuid.uuid4())[:12]}",
                    "user_id": user["user_id"],
                    "timestamp": current_time,
                    "amount": amount,
                    "currency": "USD",
                    "device_ip": user["device_ip"],
                    "latitude": user["base_lat"] + random.uniform(-0.05, 0.05),
                    "longitude": user["base_lon"] + random.uniform(-0.05, 0.05),
                    "is_fraud": False,
                    "fraud_type": None
                })
        return transactions

    def inject_velocity_attacks(self, transactions: List[Dict[str, Any]], target_count: int = 5) -> List[Dict[str, Any]]:
        selected_users = random.sample(self.users, min(target_count, len(self.users)))
        for user in selected_users:
            attack_time = self.base_date + timedelta(days=random.randint(0, 2), hours=random.randint(1, 20))
            for i in range(5):
                attack_time += timedelta(seconds=random.randint(10, 45))
                transactions.append({
                    "transaction_id": f"tx_vel_{str(uuid.uuid4())[:8]}",
                    "user_id": user["user_id"],
                    "timestamp": attack_time,
                    "amount": round(random.uniform(200.0, 999.0), 2),
                    "currency": "USD",
                    "device_ip": user["device_ip"],
                    "latitude": user["base_lat"],
                    "longitude": user["base_lon"],
                    "is_fraud": True,
                    "fraud_type": "Velocity_Attack"
                })
        return transactions

    def inject_structuring(self, transactions: List[Dict[str, Any]], target_count: int = 5) -> List[Dict[str, Any]]:
        selected_users = random.sample(self.users, min(target_count, len(self.users)))
        for user in selected_users:
            tx_time = self.base_date + timedelta(days=random.randint(0, 2))
            for _ in range(3):
                tx_time += timedelta(hours=random.randint(1, 4))
                transactions.append({
                    "transaction_id": f"tx_str_{str(uuid.uuid4())[:8]}",
                    "user_id": user["user_id"],
                    "timestamp": tx_time,
                    "amount": round(random.uniform(9500.0, 9999.0), 2),
                    "currency": "USD",
                    "device_ip": user["device_ip"],
                    "latitude": user["base_lat"],
                    "longitude": user["base_lon"],
                    "is_fraud": True,
                    "fraud_type": "Structuring_Smurfing"
                })
        return transactions

    def inject_geo_impossibility(self, transactions: List[Dict[str, Any]], target_count: int = 5) -> List[Dict[str, Any]]:
        selected_users = random.sample(self.users, min(target_count, len(self.users)))
        for user in selected_users:
            tx_time = self.base_date + timedelta(days=random.randint(0, 2))
            t1 = tx_time
            t2 = t1 + timedelta(minutes=30)
            
            transactions.append({
                "transaction_id": f"tx_geo1_{str(uuid.uuid4())[:8]}",
                "user_id": user["user_id"],
                "timestamp": t1,
                "amount": 45.00,
                "currency": "USD",
                "device_ip": user["device_ip"],
                "latitude": user["base_lat"],
                "longitude": user["base_lon"],
                "is_fraud": True,
                "fraud_type": "Geo_Impossibility_Origin"
            })
            
            transactions.append({
                "transaction_id": f"tx_geo2_{str(uuid.uuid4())[:8]}",
                "user_id": user["user_id"],
                "timestamp": t2,
                "amount": 1250.00,
                "currency": "USD",
                "device_ip": "203.0.113.55",
                "latitude": 51.5074,
                "longitude": -0.1278,
                "is_fraud": True,
                "fraud_type": "Geo_Impossibility_Jump"
            })
        return transactions

    def generate_full_dataset(self) -> List[Dict[str, Any]]:
        data = self.generate_baseline_transactions(records_per_user=15)
        data = self.inject_velocity_attacks(data)
        data = self.inject_structuring(data)
        data = self.inject_geo_impossibility(data)
        data = sorted(data, key=lambda x: x["timestamp"])
        return data
