import asyncio
import random
import uuid
from typing import Dict, Any
from enum import Enum


class PaymentProvider(str, Enum):
    MTN_MOMO = "mtn_momo"
    AIRTEL_MONEY = "airtel_money"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentService:
    """
    Simulation of Rwanda Mobile Money Gateway (MTN/Airtel)
    Handles the asynchronous push-to-pay workflow.
    """
    
    @staticmethod
    async def initiate_push_to_pay(
        phone_number: str, 
        amount: float, 
        provider: PaymentProvider
    ) -> Dict[str, Any]:
        """
        Initiates a payment request (Push USSD to customer phone)
        """
        # Generate a mock external reference
        external_id = str(uuid.uuid4())
        
        print(f"Initiating {provider.value} push to {phone_number} for {amount} RWF")
        
        # In a real scenario, this would be an API call to the provider
        # Return the reference for tracking
        return {
            "external_id": external_id,
            "status": PaymentStatus.PENDING,
            "message": f"Payment request sent to {phone_number}"
        }

    @staticmethod
    async def verify_payment(external_id: str) -> PaymentStatus:
        """
        Simulates waiting for the customer to enter their PIN.
        Returns SUCCESS, FAILED, or CANCELLED randomly for simulation.
        """
        # Simulate network latency/customer reaction time
        await asyncio.sleep(2)
        
        outcomes = [
            PaymentStatus.SUCCESSFUL, 
            PaymentStatus.SUCCESSFUL, 
            PaymentStatus.SUCCESSFUL, 
            PaymentStatus.FAILED, 
            PaymentStatus.CANCELLED
        ]
        
        return random.choice(outcomes)

    @staticmethod
    async def process_mobile_money_payment(
        phone_number: str, 
        amount: float, 
        provider: str = "MTN"
    ) -> Dict[str, Any]:
        """
        Complete end-to-end simulation of a mobile money payment.
        """
        p_provider = PaymentProvider.MTN_MOMO if "MTN" in provider.upper() else PaymentProvider.AIRTEL_MONEY
        
        # 1. Initiate Push
        initiation = await PaymentService.initiate_push_to_pay(phone_number, amount, p_provider)
        
        # 2. Simulate polling/webhook for status
        final_status = await PaymentService.verify_payment(initiation["external_id"])
        
        return {
            "external_id": initiation["external_id"],
            "status": final_status,
            "message": f"Payment {final_status.value}"
        }
