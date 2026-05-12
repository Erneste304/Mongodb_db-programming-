from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.visitor import BusinessPartner, PartnerType

router = APIRouter(prefix="/partners", tags=["partners"])


class CreatePartnerRequest(BaseModel):
    partner_id: str
    name: str
    partner_type: PartnerType
    contact_person: str
    email: str
    phone: str
    address: Optional[str] = None
    tin_number: Optional[str] = None
    contract_start_date: datetime
    contract_end_date: Optional[datetime] = None
    commission_rate: float = 0.0
    monthly_sales_target: Optional[float] = None


class PartnerResponse(BaseModel):
    id: str
    partner_id: str
    name: str
    partner_type: str
    contact_person: str
    email: str
    phone: str
    address: Optional[str]
    tin_number: Optional[str]
    contract_start_date: datetime
    contract_end_date: Optional[datetime]
    is_active: bool
    commission_rate: float
    total_sales_volume: float
    total_commission_earned: float
    on_time_delivery_rate: float
    quality_rating: float
    monthly_sales_target: Optional[float]
    monthly_sales_achieved: float
    compliance_score: float
    renewal_reminder_sent: bool


@router.post("/", response_model=PartnerResponse)
async def create_partner(request: CreatePartnerRequest):
    """Create a new business partner"""
    
    existing_partner = await BusinessPartner.find_one(BusinessPartner.partner_id == request.partner_id)
    if existing_partner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Partner ID already exists"
        )
    
    partner = BusinessPartner(**request.dict())
    await partner.insert()
    
    return PartnerResponse(
        id=str(partner.id),
        partner_id=partner.partner_id,
        name=partner.name,
        partner_type=partner.partner_type.value,
        contact_person=partner.contact_person,
        email=partner.email,
        phone=partner.phone,
        address=partner.address,
        tin_number=partner.tin_number,
        contract_start_date=partner.contract_start_date,
        contract_end_date=partner.contract_end_date,
        is_active=partner.is_active,
        commission_rate=partner.commission_rate,
        total_sales_volume=partner.total_sales_volume,
        total_commission_earned=partner.total_commission_earned,
        on_time_delivery_rate=partner.on_time_delivery_rate,
        quality_rating=partner.quality_rating,
        monthly_sales_target=partner.monthly_sales_target,
        monthly_sales_achieved=partner.monthly_sales_achieved,
        compliance_score=partner.compliance_score,
        renewal_reminder_sent=partner.renewal_reminder_sent
    )


@router.get("/", response_model=List[PartnerResponse])
async def get_partners(skip: int = 0, limit: int = 100, partner_type: Optional[PartnerType] = None, is_active: Optional[bool] = None):
    """Get all business partners with optional filtering"""
    
    query = {}
    if partner_type:
        query["partner_type"] = partner_type
    if is_active is not None:
        query["is_active"] = is_active
    
    partners = await BusinessPartner.find(query).skip(skip).limit(limit).to_list()
    
    return [
        PartnerResponse(
            id=str(p.id),
            partner_id=p.partner_id,
            name=p.name,
            partner_type=p.partner_type.value,
            contact_person=p.contact_person,
            email=p.email,
            phone=p.phone,
            address=p.address,
            tin_number=p.tin_number,
            contract_start_date=p.contract_start_date,
            contract_end_date=p.contract_end_date,
            is_active=p.is_active,
            commission_rate=p.commission_rate,
            total_sales_volume=p.total_sales_volume,
            total_commission_earned=p.total_commission_earned,
            on_time_delivery_rate=p.on_time_delivery_rate,
            quality_rating=p.quality_rating,
            monthly_sales_target=p.monthly_sales_target,
            monthly_sales_achieved=p.monthly_sales_achieved,
            compliance_score=p.compliance_score,
            renewal_reminder_sent=p.renewal_reminder_sent
        )
        for p in partners
    ]


@router.get("/{partner_id}", response_model=PartnerResponse)
async def get_partner(partner_id: str):
    """Get a specific business partner"""
    
    partner = await BusinessPartner.find_one(BusinessPartner.partner_id == partner_id)
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    return PartnerResponse(
        id=str(partner.id),
        partner_id=partner.partner_id,
        name=partner.name,
        partner_type=partner.partner_type.value,
        contact_person=partner.contact_person,
        email=partner.email,
        phone=partner.phone,
        address=partner.address,
        tin_number=partner.tin_number,
        contract_start_date=partner.contract_start_date,
        contract_end_date=partner.contract_end_date,
        is_active=partner.is_active,
        commission_rate=partner.commission_rate,
        total_sales_volume=partner.total_sales_volume,
        total_commission_earned=partner.total_commission_earned,
        on_time_delivery_rate=partner.on_time_delivery_rate,
        quality_rating=partner.quality_rating,
        monthly_sales_target=partner.monthly_sales_target,
        monthly_sales_achieved=partner.monthly_sales_achieved,
        compliance_score=partner.compliance_score,
        renewal_reminder_sent=partner.renewal_reminder_sent
    )


@router.put("/{partner_id}/performance")
async def update_partner_performance(partner_id: str, sales_volume: float, on_time_rate: float, quality_rating: float):
    """Update partner performance metrics"""
    
    partner = await BusinessPartner.find_one(BusinessPartner.partner_id == partner_id)
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    partner.total_sales_volume += sales_volume
    partner.total_commission_earned += sales_volume * (partner.commission_rate / 100)
    partner.on_time_delivery_rate = on_time_rate
    partner.quality_rating = quality_rating
    partner.updated_at = datetime.utcnow()
    await partner.save()
    
    return {"message": "Partner performance updated successfully"}


@router.post("/{partner_id}/calculate-commission")
async def calculate_commission(partner_id: str, sales_amount: float):
    """Calculate commission for a partner"""
    
    partner = await BusinessPartner.find_one(BusinessPartner.partner_id == partner_id)
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    commission = sales_amount * (partner.commission_rate / 100)
    
    return {
        "partner_id": partner.partner_id,
        "partner_name": partner.name,
        "sales_amount": sales_amount,
        "commission_rate": partner.commission_rate,
        "commission_amount": commission
    }


@router.get("/{partner_id}/performance-report")
async def get_performance_report(partner_id: str):
    """Get performance report for a partner"""
    
    partner = await BusinessPartner.find_one(BusinessPartner.partner_id == partner_id)
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    target_achievement = (partner.monthly_sales_achieved / partner.monthly_sales_target * 100) if partner.monthly_sales_target else 0
    
    return {
        "partner_id": partner.partner_id,
        "partner_name": partner.name,
        "partner_type": partner.partner_type.value,
        "total_sales_volume": partner.total_sales_volume,
        "total_commission_earned": partner.total_commission_earned,
        "on_time_delivery_rate": partner.on_time_delivery_rate,
        "quality_rating": partner.quality_rating,
        "monthly_sales_target": partner.monthly_sales_target,
        "monthly_sales_achieved": partner.monthly_sales_achieved,
        "target_achievement_percentage": target_achievement,
        "compliance_score": partner.compliance_score,
        "contract_end_date": partner.contract_end_date,
        "days_until_expiry": (partner.contract_end_date - datetime.utcnow()).days if partner.contract_end_date else None
    }


@router.put("/{partner_id}/renewal-reminder")
async def send_renewal_reminder(partner_id: str):
    """Mark renewal reminder as sent"""
    
    partner = await BusinessPartner.find_one(BusinessPartner.partner_id == partner_id)
    
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partner not found"
        )
    
    partner.renewal_reminder_sent = True
    partner.renewal_reminder_date = datetime.utcnow()
    partner.updated_at = datetime.utcnow()
    await partner.save()
    
    return {"message": "Renewal reminder sent successfully"}
