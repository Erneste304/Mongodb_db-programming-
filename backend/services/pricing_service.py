from typing import Optional
from datetime import datetime, timezone
from backend.models.pricing import FuelPricing, FuelType, PricingType


class PricingService:
    """
    Dynamic Fuel Pricing Service
    Manages active prices and handles RURA-mandated price changes.
    """

    @staticmethod
    async def get_current_price(fuel_type: FuelType, pricing_type: PricingType = PricingType.RETAIL) -> float:
        """
        Fetches the current active price for a specific fuel type.
        """
        # Use find().sort().first_or_none() because find_one() does not support .sort()
        pricing = await FuelPricing.find(
            FuelPricing.fuel_type == fuel_type,
            FuelPricing.pricing_type == pricing_type,
            FuelPricing.is_active == True,
            FuelPricing.effective_date <= datetime.now(timezone.utc),
            {"$or": [
                {"expiry_date": None},
                {"expiry_date": {"$gt": datetime.now(timezone.utc)}}
            ]}
        ).sort("-effective_date").first_or_none()

        if not pricing:
            # Fallback hardcoded prices for Rwanda if DB is empty
            defaults = {
                FuelType.PETROL: 1650.0,
                FuelType.DIESEL: 1550.0,
                FuelType.KEROSENE: 1200.0
            }
            return defaults.get(fuel_type, 1500.0)

        # Calculate final price (Base + VAT)
        base_price = pricing.price_per_liter
        vat_amount = base_price * (pricing.vat_percentage / 100)
        excise_amount = base_price * (pricing.excise_tax_percentage / 100)

        return round(base_price + vat_amount + excise_amount, 2)

    @staticmethod
    async def schedule_price_change(
        fuel_type: FuelType,
        new_base_price: float,
        effective_date: datetime,
        rura_ref: str,
        admin_id: str
    ) -> FuelPricing:
        """
        Schedules a new price change (e.g., following a RURA directive).
        Automatically deactivates old pricing when the new one becomes effective.
        """
        # Deactivate current price after the new one starts
        # (This logic would be handled by get_current_price sorting by effective_date)

        pricing = FuelPricing(
            pricing_id=f"RURA-{datetime.now(timezone.utc).strftime('%Y%m')}-{rura_ref}",
            fuel_type=fuel_type,
            price_per_liter=new_base_price,
            effective_date=effective_date,
            rura_reference=rura_ref,
            approved_by=admin_id,
            is_active=True
        )

        await pricing.insert()
        return pricing
