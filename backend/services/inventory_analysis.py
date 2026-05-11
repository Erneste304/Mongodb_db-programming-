from typing import Dict, Any, List
from datetime import datetime, timedelta
from backend.models.inventory import Tank, InventoryRecord
from backend.models.sales import Transaction


class InventoryAnalysisService:
    """
    Inventory Leakage & Theft Detection Engine
    Analyzes physical vs theoretical stock to flag suspicious activity.
    """
    
    # Threshold for variance alert (e.g., 0.5% of throughput)
    VARIANCE_TOLERANCE_PERCENT = 0.005 
    
    @staticmethod
    async def analyze_shift_variance(tank_id: str, record: InventoryRecord) -> Dict[str, Any]:
        """
        Analyzes variance for a specific shift record.
        Theoretical Closing = Opening + Deliveries - Sales
        Variance = Theoretical Closing - Actual Closing (Physical)
        """
        # 1. Calculate Theoretical Closing
        theoretical_closing = record.opening_level_liters + record.deliveries_liters - record.dispensed_liters
        
        # 2. Calculate Variance
        variance = theoretical_closing - record.closing_level_liters
        variance_percent = (abs(variance) / record.opening_level_liters) * 100 if record.opening_level_liters > 0 else 0
        
        # 3. Detect Anomalies
        is_anomaly = False
        anomaly_type = None
        severity = "low"
        
        if variance > 0: # Loss of fuel
            if variance_percent > 1.0: # Significant loss
                is_anomaly = True
                anomaly_type = "Potential Theft or Leak"
                severity = "high"
            elif variance_percent > 0.5:
                is_anomaly = True
                anomaly_type = "High Variance - Monitor"
                severity = "medium"
        elif variance < -2.0: # Gaining fuel (calibration issue or fraud)
            is_anomaly = True
            anomaly_type = "Meter/Calibration Inaccuracy"
            severity = "medium"

        return {
            "tank_id": tank_id,
            "theoretical_closing": theoretical_closing,
            "actual_closing": record.closing_level_liters,
            "variance_liters": round(variance, 2),
            "variance_percent": round(variance_percent, 2),
            "is_anomaly": is_anomaly,
            "anomaly_type": anomaly_type,
            "severity": severity,
            "timestamp": datetime.utcnow()
        }

    @staticmethod
    async def get_total_sales_for_period(tank_id: str, start_time: datetime, end_time: datetime) -> float:
        """
        Aggregates sales from transactions for a specific tank and period.
        """
        # This assumes we can link transactions to tanks via pump_id
        # For simplicity, we assume the dispensed_liters is passed in the record
        pass
