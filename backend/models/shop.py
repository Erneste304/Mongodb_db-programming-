"""
Shop/Convenience Store Models
For managing shop inventory and sales
"""

from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ShopItemCategory(str, Enum):
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    TOBACCO = "tobacco"
    AUTOMOTIVE = "automotive"
    PERSONAL_CARE = "personal_care"
    OTHER = "other"


class ShopItem(Document):
    """Shop/convenience store inventory items"""
    item_id: str = Field(..., unique=True)
    item_name: str = Field(...)
    category: ShopItemCategory
    description: Optional[str] = Field(None)
    unit_price: float = Field(..., gt=0)
    cost_price: float = Field(..., gt=0)
    current_stock: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, description="Reorder when stock below this")
    supplier: Optional[str] = Field(None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "shop_items"


class ShopSale(Document):
    """Shop sales transactions"""
    sale_id: str = Field(..., unique=True)
    customer_id: Optional[str] = Field(None)
    items: list[dict] = Field(..., description="List of {item_id, quantity, unit_price, subtotal}")
    total_amount: float = Field(..., gt=0)
    payment_method: str = Field(default="cash")
    payment_reference: Optional[str] = Field(None)
    attendant_id: Optional[str] = Field(None)
    receipt_number: Optional[str] = Field(None)
    tin_number: Optional[str] = Field(None)
    status: str = Field(default="completed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # EBM fields
    ebm_signature: Optional[str] = Field(None)
    ebm_mrc: Optional[str] = Field(None)
    ebm_internal_data: Optional[str] = Field(None)
    ebm_signed_at: Optional[datetime] = Field(None)
    
    class Settings:
        collection_name = "shop_sales"
