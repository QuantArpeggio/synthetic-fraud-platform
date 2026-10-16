from generator import SyntheticTransactionEngine
from validator import DatasetValidator

if __name__ == "__main__":
    print("=== STEP 1: Generating Synthetic Data & Injecting Fraud ===")
    engine = SyntheticTransactionEngine(num_users=30)
    raw_dataset = engine.generate_full_dataset()
    
    total_txs = len(raw_dataset)
    injected_fraud = sum(1 for tx in raw_dataset if tx["is_fraud"])
    print(f"Generated {total_txs} transactions ({injected_fraud} flagged as injected fraud).\n")

    print("=== STEP 2: Running Validation Layer ===")
    
    # 1. Schema Validation
    schema_results = DatasetValidator.validate_schema(raw_dataset)
    print(f"[Schema Check] Passed: {schema_results['passed']}/{schema_results['total_checked']} | Errors: {schema_results['failed']}")
    
    clean_data = schema_results["clean_data"]

    # 2. Geo-Velocity Check
    velocity_violations = DatasetValidator.validate_geo_velocity(clean_data, max_speed_kmh=900.0)
    print(f"[Geo-Velocity Check] Found {len(velocity_violations)} impossible travel speed violations.")

    # 3. Benford's Law Statistical Check
    benford_results = DatasetValidator.validate_benfords_law(clean_data)
    print(f"[Benford's Law Check] Status: {benford_results['message']}")
    print(f"  - Chi2 Statistic: {benford_results.get('chi2_statistic', 'N/A')}")
    print(f"  - P-Value: {benford_results.get('p_value', 'N/A')}")

    print("\n=== Pipeline Execution Complete ===")
