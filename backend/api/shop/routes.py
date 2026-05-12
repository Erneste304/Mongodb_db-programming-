from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.shop import ShopItem, ShopSale, ShopItemCategory

router = APIRouter(prefix="/shop", tags=["shop"])


class CreateShopItemRequest(BaseModel):
    item_id: str
    item_name: str
    category: ShopItemCategory
    description: Optional[str] = None
    unit_price: float
    cost_price: float
    current_stock: int = 0
    reorder_level: int = 10
    supplier: Optional[str] = None


class ShopItemResponse(BaseModel):
    id: str
    item_id: str
    item_name: str
    category: str
    description: Optional[str]
    unit_price: float
    cost_price: float
    current_stock: int
    reorder_level: int
    supplier: Optional[str]
    is_active: bool
    created_at: datetime


class CreateShopSaleRequest(BaseModel):
    sale_id: str
    customer_id: Optional[str] = None
    items: List[dict]
    payment_method: str = "cash"
    payment_reference: Optional[str] = None
    attendant_id: Optional[str] = None
    receipt_number: Optional[str] = None
    tin_number: Optional[str] = None


class ShopSaleResponse(BaseModel):
    id: str
    sale_id: str
    customer_id: Optional[str]
    items: List[dict]
    total_amount: float
    payment_method: str
    payment_reference: Optional[str]
    attendant_id: Optional[str]
    receipt_number: Optional[str]
    tin_number: Optional[str]
    status: str
    created_at: datetime


@router.post("/items", response_model=ShopItemResponse)
async def create_shop_item(request: CreateShopItemRequest):
    """Create a new shop inventory item"""
    item = ShopItem(
        item_id=request.item_id,
        item_name=request.item_name,
        category=request.category,
        description=request.description,
        unit_price=request.unit_price,
        cost_price=request.cost_price,
        current_stock=request.current_stock,
        reorder_level=request.reorder_level,
        supplier=request.supplier
    )
    
    await item.insert()
    
    return ShopItemResponse(
        id=str(item.id),
        item_id=item.item_id,
        item_name=item.item_name,
        category=item.category.value,
        description=item.description,
        unit_price=item.unit_price,
        cost_price=item.cost_price,
        current_stock=item.current_stock,
        reorder_level=item.reorder_level,
        supplier=item.supplier,
        is_active=item.is_active,
        created_at=item.created_at
    )


@router.get("/items", response_model=List[ShopItemResponse])
async def get_shop_items(skip: int = 0, limit: int = 100, category: Optional[ShopItemCategory] = None):
    """Get all shop items with optional filtering"""
    query = {"is_active": True}
    if category:
        query["category"] = category
    
    items = await ShopItem.find(query).skip(skip).limit(limit).to_list()
    
    return [
        ShopItemResponse(
            id=str(i.id),
            item_id=i.item_id,
            item_name=i.item_name,
            category=i.category.value,
            description=i.description,
            unit_price=i.unit_price,
            cost_price=i.cost_price,
            current_stock=i.current_stock,
            reorder_level=i.reorder_level,
            supplier=i.supplier,
            is_active=i.is_active,
            created_at=i.created_at
        )
        for i in items
    ]


@router.post("/sales", response_model=ShopSaleResponse)
async def create_shop_sale(request: CreateShopSaleRequest):
    """Create a new shop sale"""
    total_amount = sum(item.get("subtotal", 0) for item in request.items)
    
    sale = ShopSale(
        sale_id=request.sale_id,
        customer_id=request.customer_id,
        items=request.items,
        total_amount=total_amount,
        payment_method=request.payment_method,
        payment_reference=request.payment_reference,
        attendant_id=request.attendant_id,
        receipt_number=request.receipt_number,
        tin_number=request.tin_number
    )
    
    # Update stock for each item
    for item in request.items:
        shop_item = await ShopItem.find_one(ShopItem.item_id == item.get("item_id"))
        if shop_item:
            shop_item.current_stock -= item.get("quantity", 0)
            await shop_item.save()
    
    await sale.insert()
    
    return ShopSaleResponse(
        id=str(sale.id),
        sale_id=sale.sale_id,
        customer_id=sale.customer_id,
        items=sale.items,
        total_amount=sale.total_amount,
        payment_method=sale.payment_method,
        payment_reference=sale.payment_reference,
        attendant_id=sale.attendant_id,
        receipt_number=sale.receipt_number,
        tin_number=sale.tin_number,
        status=sale.status,
        created_at=sale.created_at
    )


@router.get("/sales", response_model=List[ShopSaleResponse])
async def get_shop_sales(skip: int = 0, limit: int = 100):
    """Get all shop sales"""
    sales = await ShopSale.find_all().skip(skip).limit(limit).sort("-created_at").to_list()
    
    return [
        ShopSaleResponse(
            id=str(s.id),
            sale_id=s.sale_id,
            customer_id=s.customer_id,
            items=s.items,
            total_amount=s.total_amount,
            payment_method=s.payment_method,
            payment_reference=s.payment_reference,
            attendant_id=s.attendant_id,
            receipt_number=s.receipt_number,
            tin_number=s.tin_number,
            status=s.status,
            created_at=s.created_at
        )
        for s in sales
    ]
