import hashlib
import random
import string
from datetime import datetime
from typing import Dict, Any
from backend.models.sales import Transaction


class TaxService:
    """
    RRA EBM (Electronic Billing Machine) Integration Service
    Handles tax calculation and receipt signing according to Rwanda Revenue Authority protocols.
    """
    
    VAT_RATE = 0.18  # Rwanda VAT 18%
    MRC = "EBM-V2-88000456"  # Mock Machine Record Code
    
    @staticmethod
    def calculate_vat(total_amount: float) -> Dict[str, float]:
        """
        Calculate VAT amount from total (inclusive)
        VAT = Total - (Total / 1.18)
        """
        net_amount = total_amount / (1 + TaxService.VAT_RATE)
        vat_amount = total_amount - net_amount
        return {
            "net_amount": round(net_amount, 2),
            "vat_amount": round(vat_amount, 2)
        }
    
    @staticmethod
    def generate_ebm_signature(transaction: Transaction) -> str:
        """
        Generates a unique SCD (Signature) for the transaction.
        In a real scenario, this would be an API call to RRA.
        """
        data_string = f"{transaction.transaction_id}|{transaction.total_amount}|{transaction.created_at.isoformat()}|{TaxService.MRC}"
        signature = hashlib.sha256(data_string.encode()).hexdigest().upper()[:16]
        
        # Format: XXXX-XXXX-XXXX-XXXX
        return "-".join([signature[i:i+4] for i in range(0, 16, 4)])

    @staticmethod
    def generate_internal_data() -> str:
        """Generates random EBM internal data string"""
        chars = string.ascii_uppercase + string.digits
        return "".join(random.choice(chars) for _ in range(20))

    @staticmethod
    async def sign_transaction(transaction: Transaction) -> Transaction:
        """
        Process a transaction through the virtual EBM.
        Calculates VAT and attaches official signing data.
        """
        # 1. Calculate Tax
        tax_info = TaxService.calculate_vat(transaction.total_amount)
        transaction.net_amount = tax_info["net_amount"]
        transaction.vat_amount = tax_info["vat_amount"]
        
        # 2. Generate EBM Identifiers
        transaction.ebm_signature = TaxService.generate_ebm_signature(transaction)
        transaction.ebm_mrc = TaxService.MRC
        transaction.ebm_internal_data = TaxService.generate_internal_data()
        transaction.ebm_signed_at = datetime.utcnow()
        
        # 3. Generate Receipt Number if missing
        if not transaction.receipt_number:
            transaction.receipt_number = f"EBM-{transaction.created_at.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            
        return transaction
