from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from backend.models.sales import Transaction, FuelType
from backend.models.inventory import Tank
from backend.models.finance import Payment, DailyCashReconciliation

router = APIRouter(prefix="/reports", tags=["reports"])


class SalesReportResponse(BaseModel):
    period: str
    total_sales: float
    total_transactions: int
    sales_by_fuel_type: dict
    sales_by_payment_method: dict
    average_transaction_value: float


class InventoryReportResponse(BaseModel):
    report_date: datetime
    total_tanks: int
    total_capacity: float
    total_current_level: float
    average_fill_percentage: float
    tanks_below_threshold: list


class FinancialReportResponse(BaseModel):
    period: str
    total_revenue: float
    total_expenses: float
    net_profit: float
    pending_payments: float
    approved_payments: float
    processed_payments: float


class DailySummaryResponse(BaseModel):
    date: datetime
    total_sales: float
    total_transactions: int
    cash_sales: float
    mobile_money_sales: float
    card_sales: float
    credit_sales: float
    fuel_dispensed_liters: float
    inventory_variance: float


@router.get("/sales/daily", response_model=SalesReportResponse)
async def get_daily_sales_report(date: Optional[datetime] = None):
    """Get daily sales report"""
    
    if date is None:
        date = datetime.utcnow()
    
    start_of_day = datetime(date.year, date.month, date.day)
    end_of_day = start_of_day + timedelta(days=1)
    
    # Get transactions for the day
    transactions = await Transaction.find(
        Transaction.created_at >= start_of_day,
        Transaction.created_at < end_of_day,
        Transaction.status == "completed"
    ).to_list()
    
    total_sales = sum(tx.total_amount for tx in transactions)
    total_transactions = len(transactions)
    average_transaction_value = total_sales / total_transactions if total_transactions > 0 else 0
    
    # Sales by fuel type
    sales_by_fuel_type = {}
    for tx in transactions:
        fuel_type = tx.fuel_type.value
        sales_by_fuel_type[fuel_type] = sales_by_fuel_type.get(fuel_type, 0) + tx.total_amount
    
    # Sales by payment method
    sales_by_payment_method = {}
    for tx in transactions:
        payment_method = tx.payment_method.value
        sales_by_payment_method[payment_method] = sales_by_payment_method.get(payment_method, 0) + tx.total_amount
    
    return SalesReportResponse(
        period=date.strftime("%Y-%m-%d"),
        total_sales=total_sales,
        total_transactions=total_transactions,
        sales_by_fuel_type=sales_by_fuel_type,
        sales_by_payment_method=sales_by_payment_method,
        average_transaction_value=average_transaction_value
    )


@router.get("/sales/weekly", response_model=SalesReportResponse)
async def get_weekly_sales_report():
    """Get weekly sales report"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    # Get transactions for the week
    transactions = await Transaction.find(
        Transaction.created_at >= start_date,
        Transaction.created_at < end_date,
        Transaction.status == "completed"
    ).to_list()
    
    total_sales = sum(tx.total_amount for tx in transactions)
    total_transactions = len(transactions)
    average_transaction_value = total_sales / total_transactions if total_transactions > 0 else 0
    
    # Sales by fuel type
    sales_by_fuel_type = {}
    for tx in transactions:
        fuel_type = tx.fuel_type.value
        sales_by_fuel_type[fuel_type] = sales_by_fuel_type.get(fuel_type, 0) + tx.total_amount
    
    # Sales by payment method
    sales_by_payment_method = {}
    for tx in transactions:
        payment_method = tx.payment_method.value
        sales_by_payment_method[payment_method] = sales_by_payment_method.get(payment_method, 0) + tx.total_amount
    
    return SalesReportResponse(
        period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        total_sales=total_sales,
        total_transactions=total_transactions,
        sales_by_fuel_type=sales_by_fuel_type,
        sales_by_payment_method=sales_by_payment_method,
        average_transaction_value=average_transaction_value
    )


@router.get("/sales/monthly", response_model=SalesReportResponse)
async def get_monthly_sales_report(year: int, month: int):
    """Get monthly sales report"""
    
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Get transactions for the month
    transactions = await Transaction.find(
        Transaction.created_at >= start_date,
        Transaction.created_at < end_date,
        Transaction.status == "completed"
    ).to_list()
    
    total_sales = sum(tx.total_amount for tx in transactions)
    total_transactions = len(transactions)
    average_transaction_value = total_sales / total_transactions if total_transactions > 0 else 0
    
    # Sales by fuel type
    sales_by_fuel_type = {}
    for tx in transactions:
        fuel_type = tx.fuel_type.value
        sales_by_fuel_type[fuel_type] = sales_by_fuel_type.get(fuel_type, 0) + tx.total_amount
    
    # Sales by payment method
    sales_by_payment_method = {}
    for tx in transactions:
        payment_method = tx.payment_method.value
        sales_by_payment_method[payment_method] = sales_by_payment_method.get(payment_method, 0) + tx.total_amount
    
    return SalesReportResponse(
        period=f"{year}-{month:02d}",
        total_sales=total_sales,
        total_transactions=total_transactions,
        sales_by_fuel_type=sales_by_fuel_type,
        sales_by_payment_method=sales_by_payment_method,
        average_transaction_value=average_transaction_value
    )


@router.get("/inventory/current", response_model=InventoryReportResponse)
async def get_current_inventory_report():
    """Get current inventory report"""
    
    tanks = await Tank.find(Tank.status == "active").to_list()
    
    total_tanks = len(tanks)
    total_capacity = sum(tank.capacity_liters for tank in tanks)
    total_current_level = sum(tank.current_level_liters for tank in tanks)
    average_fill_percentage = (total_current_level / total_capacity * 100) if total_capacity > 0 else 0
    
    # Tanks below threshold
    tanks_below_threshold = []
    for tank in tanks:
        fill_percentage = (tank.current_level_liters / tank.capacity_liters * 100) if tank.capacity_liters > 0 else 0
        if fill_percentage < tank.threshold_alert_percent:
            tanks_below_threshold.append({
                "tank_id": tank.tank_id,
                "tank_number": tank.tank_number,
                "fuel_type": tank.fuel_type.value,
                "current_level": tank.current_level_liters,
                "capacity": tank.capacity_liters,
                "fill_percentage": fill_percentage
            })
    
    return InventoryReportResponse(
        report_date=datetime.utcnow(),
        total_tanks=total_tanks,
        total_capacity=total_capacity,
        total_current_level=total_current_level,
        average_fill_percentage=average_fill_percentage,
        tanks_below_threshold=tanks_below_threshold
    )


@router.get("/finance/summary", response_model=FinancialReportResponse)
async def get_financial_summary_report():
    """Get financial summary report"""
    
    # Get current month's data
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)
    
    # Get payments
    payments = await Payment.find(
        Payment.requested_at >= start_of_month
    ).to_list()
    
    total_expenses = sum(payment.amount for payment in payments if payment.status == "processed")
    pending_payments = sum(payment.amount for payment in payments if payment.status == "pending")
    approved_payments = sum(payment.amount for payment in payments if payment.status == "approved")
    processed_payments = sum(payment.amount for payment in payments if payment.status == "processed")
    
    # Get sales revenue
    transactions = await Transaction.find(
        Transaction.created_at >= start_of_month,
        Transaction.status == "completed"
    ).to_list()
    total_revenue = sum(tx.total_amount for tx in transactions)
    
    net_profit = total_revenue - total_expenses
    
    return FinancialReportResponse(
        period=f"{now.year}-{now.month:02d}",
        total_revenue=total_revenue,
        total_expenses=total_expenses,
        net_profit=net_profit,
        pending_payments=pending_payments,
        approved_payments=approved_payments,
        processed_payments=processed_payments
    )


@router.get("/daily-summary", response_model=DailySummaryResponse)
async def get_daily_summary(date: Optional[datetime] = None):
    """Get comprehensive daily summary"""
    
    if date is None:
        date = datetime.utcnow()
    
    start_of_day = datetime(date.year, date.month, date.day)
    end_of_day = start_of_day + timedelta(days=1)
    
    # Get transactions
    transactions = await Transaction.find(
        Transaction.created_at >= start_of_day,
        Transaction.created_at < end_of_day,
        Transaction.status == "completed"
    ).to_list()
    
    total_sales = sum(tx.total_amount for tx in transactions)
    total_transactions = len(transactions)
    
    # Sales by payment method
    cash_sales = sum(tx.total_amount for tx in transactions if tx.payment_method.value == "cash")
    mobile_money_sales = sum(tx.total_amount for tx in transactions if tx.payment_method.value == "mobile_money")
    card_sales = sum(tx.total_amount for tx in transactions if tx.payment_method.value == "card")
    credit_sales = sum(tx.total_amount for tx in transactions if tx.payment_method.value == "credit")
    
    # Fuel dispensed
    fuel_dispensed_liters = sum(tx.quantity_liters for tx in transactions)
    
    # Get reconciliation if available
    reconciliation = await DailyCashReconciliation.find_one(
        DailyCashReconciliation.date >= start_of_day,
        DailyCashReconciliation.date < end_of_day
    )
    
    inventory_variance = reconciliation.variance if reconciliation else 0
    
    return DailySummaryResponse(
        date=date,
        total_sales=total_sales,
        total_transactions=total_transactions,
        cash_sales=cash_sales,
        mobile_money_sales=mobile_money_sales,
        card_sales=card_sales,
        credit_sales=credit_sales,
        fuel_dispensed_liters=fuel_dispensed_liters,
        inventory_variance=inventory_variance
    )
