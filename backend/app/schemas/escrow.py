"""
escrow.py — Cấu hình Schemas Phản hồi & Yêu cầu cho Ví Ký Quỹ Escrow & Sổ cái 24/7
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class EscrowWalletResponse(BaseModel):
    """Schema chuẩn trả về số dư Ví Ký Quỹ Escrow."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    available_balance: float
    locked_balance: float
    total_withdrawn: float
    total_balance: float
    currency: str = "VND"
    updated_at: Optional[datetime] = None


class EscrowTransactionResponse(BaseModel):
    """Schema chuẩn bản ghi giao dịch sổ cái đối soát."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    wallet_id: int
    order_id: Optional[int] = None
    transaction_code: str
    type: str
    amount: float
    balance_before: float
    balance_after: float
    description: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None


class WithdrawalRequest(BaseModel):
    amount: float = Field(..., gt=50000, description="Số tiền muốn rút (tối thiểu 50.000đ)")
    bank_account_id: int
    note: Optional[str] = None
