from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.lubricant import LubricantItem, LubricantStockCount, LubricantCategory

router = APIRouter(prefix="/lubricant", tags=["lubricant"])


class CreateLubricantItemRequest(BaseModel):
    item_id: str
    item_name: str
    category: LubricantCategory
    brand: Optional[str] = None
    specification: Optional[str] = None
    current_stock: float = 0
    unit_of_measure: str = "liters"
    reorder_level: float = 50
    max_stock: float = 500
    cost_price: float
    selling_price: float
    storage_location: Optional[str] = None
    storage_conditions: Optional[str] = None
    expiry_date: Optional[datetime] = None
    supplier: Optional[str] = None
    supplier_code: Optional[str] = None


class LubricantItemResponse(BaseModel):
    id: str
    item_id: str
    item_name: str
    category: str
    brand: Optional[str]
    specification: Optional[str]
    current_stock: float
    unit_of_measure: str
    reorder_level: float
    max_stock: float
    cost_price: float
    selling_price: float
    storage_location: Optional[str]
    storage_conditions: Optional[str]
    expiry_date: Optional[datetime]
    supplier: Optional[str]
    supplier_code: Optional[str]
    is_active: bool


class CreateLubricantStockCountRequest(BaseModel):
    count_id: str
    item_id: str
    counted_quantity: float
    counted_by: str
    count_type: str = "regular"
    discrepancy_reason: Optional[str] = None
    action_taken: Optional[str] = None
    notes: Optional[str] = None


class LubricantStockCountResponse(BaseModel):
    id: str
    count_id: str
    item_id: str
    item_name: str
    counted_quantity: float
    system_quantity: float
    variance: float
    variance_percentage: float
    counted_by: str
    counted_at: datetime
    count_type: str
    discrepancy_reason: Optional[str]
    action_taken: Optional[str]
    notes: Optional[str]


@router.post("/items", response_model=LubricantItemResponse)
async def create_lubricant_item(request: CreateLubricantItemRequest):
    """Create a new lubricant item"""
    
    existing_item = await LubricantItem.find_one(LubricantItem.item_id == request.item_id)
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item ID already exists"
        )
    
    item = LubricantItem(**request.dict())
    await item.insert()
    
    return LubricantItemResponse(
        id=str(item.id),
        item_id=item.item_id,
        item_name=item.item_name,
        category=item.category.value,
        brand=item.brand,
        specification=item.specification,
        current_stock=item.current_stock,
        unit_of_measure=item.unit_of_measure,
        reorder_level=item.reorder_level,
        max_stock=item.max_stock,
        cost_price=item.cost_price,
        selling_price=item.selling_price,
        storage_location=item.storage_location,
        storage_conditions=item.storage_conditions,
        expiry_date=item.expiry_date,
        supplier=item.supplier,
        supplier_code=item.supplier_code,
        is_active=item.is_active
    )


@router.get("/items", response_model=List[LubricantItemResponse])
async def get_lubricant_items(skip: int = 0, limit: int = 100, category: Optional[LubricantCategory] = None):
    """Get all lubricant items with optional filtering"""
    
    query = {"is_active": True}
    if category:
        query["category"] = category
    
    items = await LubricantItem.find(query).skip(skip).limit(limit).to_list()
    
    return [
        LubricantItemResponse(
            id=str(i.id),
            item_id=i.item_id,
            item_name=i.item_name,
            category=i.category.value,
            brand=i.brand,
            specification=i.specification,
            current_stock=i.current_stock,
            unit_of_measure=i.unit_of_measure,
            reorder_level=i.reorder_level,
            max_stock=i.max_stock,
            cost_price=i.cost_price,
            selling_price=i.selling_price,
            storage_location=i.storage_location,
            storage_conditions=i.storage_conditions,
            expiry_date=i.expiry_date,
            supplier=i.supplier,
            supplier_code=i.supplier_code,
            is_active=i.is_active
        )
        for i in items
    ]


@router.get("/items/{item_id}", response_model=LubricantItemResponse)
async def get_lubricant_item(item_id: str):
    """Get a specific lubricant item"""
    
    item = await LubricantItem.find_one(LubricantItem.item_id == item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    return LubricantItemResponse(
        id=str(item.id),
        item_id=item.item_id,
        item_name=item.item_name,
        category=item.category.value,
        brand=item.brand,
        specification=item.specification,
        current_stock=item.current_stock,
        unit_of_measure=item.unit_of_measure,
        reorder_level=item.reorder_level,
        max_stock=item.max_stock,
        cost_price=item.cost_price,
        selling_price=item.selling_price,
        storage_location=item.storage_location,
        storage_conditions=item.storage_conditions,
        expiry_date=item.expiry_date,
        supplier=item.supplier,
        supplier_code=item.supplier_code,
        is_active=item.is_active
    )


@router.patch("/items/{item_id}", response_model=LubricantItemResponse)
async def update_lubricant_item(item_id: str, request: dict):
    """Update lubricant item"""
    
    item = await LubricantItem.find_one(LubricantItem.item_id == item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    for key, value in request.items():
        if hasattr(item, key):
            setattr(item, key, value)
    
    item.updated_at = datetime.utcnow()
    await item.save()
    
    return LubricantItemResponse(
        id=str(item.id),
        item_id=item.item_id,
        item_name=item.item_name,
        category=item.category.value,
        brand=item.brand,
        specification=item.specification,
        current_stock=item.current_stock,
        unit_of_measure=item.unit_of_measure,
        reorder_level=item.reorder_level,
        max_stock=item.max_stock,
        cost_price=item.cost_price,
        selling_price=item.selling_price,
        storage_location=item.storage_location,
        storage_conditions=item.storage_conditions,
        expiry_date=item.expiry_date,
        supplier=item.supplier,
        supplier_code=item.supplier_code,
        is_active=item.is_active
    )


@router.post("/stock-counts", response_model=LubricantStockCountResponse)
async def create_lubricant_stock_count(request: CreateLubricantStockCountRequest):
    """Create a lubricant stock count"""
    
    item = await LubricantItem.find_one(LubricantItem.item_id == request.item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    existing_count = await LubricantStockCount.find_one(LubricantStockCount.count_id == request.count_id)
    if existing_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Count ID already exists"
        )
    
    variance = request.counted_quantity - item.current_stock
    variance_percentage = (variance / item.current_stock * 100) if item.current_stock > 0 else 0
    
    count = LubricantStockCount(
        count_id=request.count_id,
        item_id=request.item_id,
        item_name=item.item_name,
        counted_quantity=request.counted_quantity,
        system_quantity=item.current_stock,
        variance=variance,
        variance_percentage=variance_percentage,
        counted_by=request.counted_by,
        count_type=request.count_type,
        discrepancy_reason=request.discrepancy_reason,
        action_taken=request.action_taken,
        notes=request.notes
    )
    
    await count.insert()
    
    # Update item stock if count is verified
    # item.current_stock = request.counted_quantity
    # await item.save()
    
    return LubricantStockCountResponse(
        id=str(count.id),
        count_id=count.count_id,
        item_id=count.item_id,
        item_name=count.item_name,
        counted_quantity=count.counted_quantity,
        system_quantity=count.system_quantity,
        variance=count.variance,
        variance_percentage=count.variance_percentage,
        counted_by=count.counted_by,
        counted_at=count.counted_at,
        count_type=count.count_type,
        discrepancy_reason=count.discrepancy_reason,
        action_taken=count.action_taken,
        notes=count.notes
    )


@router.get("/stock-counts", response_model=List[LubricantStockCountResponse])
async def get_lubricant_stock_counts(skip: int = 0, limit: int = 100, item_id: Optional[str] = None):
    """Get all lubricant stock counts with optional filtering"""
    
    query = {}
    if item_id:
        query["item_id"] = item_id
    
    counts = await LubricantStockCount.find(query).skip(skip).limit(limit).sort("-counted_at").to_list()
    
    return [
        LubricantStockCountResponse(
            id=str(c.id),
            count_id=c.count_id,
            item_id=c.item_id,
            item_name=c.item_name,
            counted_quantity=c.counted_quantity,
            system_quantity=c.system_quantity,
            variance=c.variance,
            variance_percentage=c.variance_percentage,
            counted_by=c.counted_by,
            counted_at=c.counted_at,
            count_type=c.count_type,
            discrepancy_reason=c.discrepancy_reason,
            action_taken=c.action_taken,
            notes=c.notes
        )
        for c in counts
    ]
