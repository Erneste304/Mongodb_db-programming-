"""
Pricing and Partner Management API Routes
Superadmin controls for fuel pricing and partner agreements
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.pricing import FuelPricing, PartnerAgreement, FuelType, PricingType
from backend.core.security import get_current_user, require_role_level
from backend.models.user import User
from backend.services.audit_service import AuditLogService

router = APIRouter(prefix="/pricing", tags=["pricing"])


# ==================== FUEL PRICING ====================

class CreateFuelPricingRequest(BaseModel):
    fuel_type: FuelType
    pricing_type: PricingType = PricingType.RETAIL
    price_per_liter: float
    vat_percentage: float = 18
    excise_tax_percentage: float = 0
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    rura_reference: Optional[str] = None
    notes: Optional[str] = None


class UpdateFuelPricingRequest(BaseModel):
    price_per_liter: Optional[float] = None
    vat_percentage: Optional[float] = None
    expiry_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class FuelPricingResponse(BaseModel):
    id: str
    fuel_type: str
    pricing_type: str
    price_per_liter: float
    final_price: float
    vat_percentage: float
    excise_tax_percentage: float
    effective_date: datetime
    expiry_date: Optional[datetime]
    is_active: bool
    approved_by: str
    rura_reference: Optional[str]


@router.post("/fuel", response_model=FuelPricingResponse)
async def create_fuel_pricing(
    request: CreateFuelPricingRequest,
    current_user: User = Depends(require_role_level(1))
):
    """Create new fuel pricing - SUPERADMIN ONLY"""
    
    # Calculate final price with VAT and taxes
    base_price = request.price_per_liter
    vat_amount = base_price * (request.vat_percentage / 100)
    excise_amount = base_price * (request.excise_tax_percentage / 100)
    final_price = base_price + vat_amount + excise_amount
    
    pricing = FuelPricing(
        pricing_id=f"PRICE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        fuel_type=request.fuel_type,
        pricing_type=request.pricing_type,
        price_per_liter=request.price_per_liter,
        vat_percentage=request.vat_percentage,
        excise_tax_percentage=request.excise_tax_percentage,
        effective_date=request.effective_date or datetime.utcnow(),
        expiry_date=request.expiry_date,
        is_active=True,
        approved_by=str(current_user.id),
        rura_reference=request.rura_reference,
        notes=request.notes
    )
    
    await pricing.insert()
    
    # Log the action
    await AuditLogService.log_action(
        user=current_user,
        action="created_fuel_pricing",
        resource_type="fuel_pricing",
        resource_id=str(pricing.id),
        old_value={},
        new_value={
            "fuel_type": request.fuel_type.value,
            "price_per_liter": request.price_per_liter,
            "final_price": final_price
        }
    )
    
    return FuelPricingResponse(
        id=str(pricing.id),
        fuel_type=pricing.fuel_type.value,
        pricing_type=pricing.pricing_type.value,
        price_per_liter=pricing.price_per_liter,
        final_price=final_price,
        vat_percentage=pricing.vat_percentage,
        excise_tax_percentage=pricing.excise_tax_percentage,
        effective_date=pricing.effective_date,
        expiry_date=pricing.expiry_date,
        is_active=pricing.is_active,
        approved_by=pricing.approved_by,
        rura_reference=pricing.rura_reference
    )


@router.get("/fuel/current", response_model=List[FuelPricingResponse])
async def get_current_pricing(
    fuel_type: Optional[FuelType] = None,
    current_user: User = Depends(get_current_user)
):
    """Get current active fuel pricing"""
    
    query = {"is_active": True, "expiry_date": None}
    if fuel_type:
        query["fuel_type"] = fuel_type
    
    pricing_list = await FuelPricing.find(query).to_list()
    
    responses = []
    for pricing in pricing_list:
        base_price = pricing.price_per_liter
        vat_amount = base_price * (pricing.vat_percentage / 100)
        excise_amount = base_price * (pricing.excise_tax_percentage / 100)
        final_price = base_price + vat_amount + excise_amount
        
        responses.append(FuelPricingResponse(
            id=str(pricing.id),
            fuel_type=pricing.fuel_type.value,
            pricing_type=pricing.pricing_type.value,
            price_per_liter=pricing.price_per_liter,
            final_price=final_price,
            vat_percentage=pricing.vat_percentage,
            excise_tax_percentage=pricing.excise_tax_percentage,
            effective_date=pricing.effective_date,
            expiry_date=pricing.expiry_date,
            is_active=pricing.is_active,
            approved_by=pricing.approved_by,
            rura_reference=pricing.rura_reference
        ))
    
    return responses


@router.put("/fuel/{pricing_id}", response_model=FuelPricingResponse)
async def update_fuel_pricing(
    pricing_id: str,
    request: UpdateFuelPricingRequest,
    current_user: User = Depends(require_role_level(1))
):
    """Update fuel pricing - SUPERADMIN ONLY"""
    
    pricing = await FuelPricing.find_one({"pricing_id": pricing_id})
    if not pricing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricing not found"
        )
    
    old_values = {
        "price_per_liter": pricing.price_per_liter,
        "vat_percentage": pricing.vat_percentage,
        "is_active": pricing.is_active
    }
    
    # Update fields
    if request.price_per_liter is not None:
        pricing.price_per_liter = request.price_per_liter
    if request.vat_percentage is not None:
        pricing.vat_percentage = request.vat_percentage
    if request.expiry_date is not None:
        pricing.expiry_date = request.expiry_date
    if request.is_active is not None:
        pricing.is_active = request.is_active
    
    await pricing.save()
    
    # Log the action
    await AuditLogService.log_action(
        user=current_user,
        action="updated_fuel_pricing",
        resource_type="fuel_pricing",
        resource_id=str(pricing.id),
        old_value=old_values,
        new_value={
            "price_per_liter": pricing.price_per_liter,
            "vat_percentage": pricing.vat_percentage,
            "is_active": pricing.is_active
        }
    )
    
    base_price = pricing.price_per_liter
    vat_amount = base_price * (pricing.vat_percentage / 100)
    excise_amount = base_price * (pricing.excise_tax_percentage / 100)
    final_price = base_price + vat_amount + excise_amount
    
    return FuelPricingResponse(
        id=str(pricing.id),
        fuel_type=pricing.fuel_type.value,
        pricing_type=pricing.pricing_type.value,
        price_per_liter=pricing.price_per_liter,
        final_price=final_price,
        vat_percentage=pricing.vat_percentage,
        excise_tax_percentage=pricing.excise_tax_percentage,
        effective_date=pricing.effective_date,
        expiry_date=pricing.expiry_date,
        is_active=pricing.is_active,
        approved_by=pricing.approved_by,
        rura_reference=pricing.rura_reference
    )


# ==================== PARTNER AGREEMENTS ====================

class CreatePartnerAgreementRequest(BaseModel):
    partner_name: str
    partner_type: str
    agreement_start_date: datetime
    agreement_end_date: Optional[datetime] = None
    commission_percentage: float = 0
    credit_terms_days: int = 30
    minimum_order_quantity: float = 0
    discount_percentage: float = 0
    contact_person: str
    contact_email: str
    contact_phone: str
    notes: Optional[str] = None


class PartnerAgreementResponse(BaseModel):
    id: str
    agreement_id: str
    partner_name: str
    partner_type: str
    agreement_start_date: datetime
    agreement_end_date: Optional[datetime]
    commission_percentage: float
    credit_terms_days: int
    is_active: bool
    contact_person: str


@router.post("/partners", response_model=PartnerAgreementResponse)
async def create_partner_agreement(
    request: CreatePartnerAgreementRequest,
    current_user: User = Depends(require_role_level(1))
):
    """Create partner agreement - SUPERADMIN ONLY"""
    
    agreement = PartnerAgreement(
        agreement_id=f"AGREE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        partner_name=request.partner_name,
        partner_type=request.partner_type,
        agreement_start_date=request.agreement_start_date,
        agreement_end_date=request.agreement_end_date,
        commission_percentage=request.commission_percentage,
        credit_terms_days=request.credit_terms_days,
        minimum_order_quantity=request.minimum_order_quantity,
        discount_percentage=request.discount_percentage,
        is_active=True,
        contact_person=request.contact_person,
        contact_email=request.contact_email,
        contact_phone=request.contact_phone,
        notes=request.notes,
        approved_by=str(current_user.id)
    )
    
    await agreement.insert()
    
    # Log the action
    await AuditLogService.log_action(
        user=current_user,
        action="created_partner_agreement",
        resource_type="partner_agreement",
        resource_id=str(agreement.id),
        old_value={},
        new_value={
            "partner_name": request.partner_name,
            "partner_type": request.partner_type,
            "commission": request.commission_percentage
        }
    )
    
    return PartnerAgreementResponse(
        id=str(agreement.id),
        agreement_id=agreement.agreement_id,
        partner_name=agreement.partner_name,
        partner_type=agreement.partner_type,
        agreement_start_date=agreement.agreement_start_date,
        agreement_end_date=agreement.agreement_end_date,
        commission_percentage=agreement.commission_percentage,
        credit_terms_days=agreement.credit_terms_days,
        is_active=agreement.is_active,
        contact_person=agreement.contact_person
    )


@router.get("/partners", response_model=List[PartnerAgreementResponse])
async def get_partner_agreements(
    partner_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user)
):
    """Get all partner agreements"""
    
    query = {}
    if partner_type:
        query["partner_type"] = partner_type
    if is_active is not None:
        query["is_active"] = is_active
    
    agreements = await PartnerAgreement.find(query).to_list()
    
    return [
        PartnerAgreementResponse(
            id=str(agreement.id),
            agreement_id=agreement.agreement_id,
            partner_name=agreement.partner_name,
            partner_type=agreement.partner_type,
            agreement_start_date=agreement.agreement_start_date,
            agreement_end_date=agreement.agreement_end_date,
            commission_percentage=agreement.commission_percentage,
            credit_terms_days=agreement.credit_terms_days,
            is_active=agreement.is_active,
            contact_person=agreement.contact_person
        )
        for agreement in agreements
    ]
