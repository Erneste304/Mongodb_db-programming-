from typing import List, Dict, Any
from datetime import datetime, timedelta
from backend.models.sales import Transaction, Customer, FuelType


class LoyaltyAIService:
    """
    AI-Driven Customer Loyalty & Retention System
    Analyzes behavior to provide personalized incentives.
    """
    
    @staticmethod
    async def analyze_customer_profile(customer: Customer) -> Dict[str, Any]:
        """
        Analyzes customer history to determine segment and personalized offers.
        """
        # 1. Segment Detection
        segment = "Standard"
        if customer.customer_type == "cash":
            segment = "One-time"
        elif customer.loyalty_points > 1000:
            segment = "Premium"
        
        # 2. Pattern Analysis (Simulated)
        # In a real scenario, we would query historical transactions
        offers = []
        
        # Scenario: Moto-Taxi Retention
        if "moto" in (customer.name.lower() or ""):
            offers.append({
                "type": "BOOSTER",
                "name": "Moto-Taxi Monday",
                "description": "2x Points on Mondays",
                "multiplier": 2.0
            })
            
        # Scenario: Bulk Purchase Incentive
        offers.append({
            "type": "DISCOUNT",
            "name": "Volume Bonus",
            "description": "10 RWF off per liter for orders > 50L",
            "threshold": 50.0,
            "discount_per_liter": 10.0
        })
        
        return {
            "customer_id": customer.customer_id,
            "segment": segment,
            "active_offers": offers,
            "last_analysis": datetime.utcnow()
        }

    @staticmethod
    def calculate_points_earned(total_amount: float, multiplier: float = 1.0) -> int:
        """
        Standard Points: 1 point per 1000 RWF spent
        """
        base_points = int(total_amount / 1000)
        return int(base_points * multiplier)

    @staticmethod
    async def apply_loyalty_rewards(transaction: Transaction, customer: Customer) -> Dict[str, Any]:
        """
        Applies loyalty boosters and points to a transaction.
        """
        analysis = await LoyaltyAIService.analyze_customer_profile(customer)
        
        multiplier = 1.0
        discount = 0.0
        
        for offer in analysis["active_offers"]:
            # Apply multipliers
            if offer["type"] == "BOOSTER":
                # Check if today matches booster conditions (e.g., Monday)
                if datetime.utcnow().weekday() == 0: # Monday
                    multiplier = offer["multiplier"]
            
            # Apply discounts
            if offer["type"] == "DISCOUNT":
                if transaction.quantity_liters >= offer["threshold"]:
                    discount = transaction.quantity_liters * offer["discount_per_liter"]
        
        points_earned = LoyaltyAIService.calculate_points_earned(transaction.total_amount, multiplier)
        
        return {
            "points_earned": points_earned,
            "discount_applied": discount,
            "applied_offers": [o["name"] for o in analysis["active_offers"]]
        }
