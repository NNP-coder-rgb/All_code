"""
models/escrow.py — Models SQLAlchemy cho Ví Ký Quỹ Escrow & Sổ Cái Biến Động Dòng Tiền 24/7
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, BigInteger, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class EscrowWallet(Base):
    """Bảng 16: escrow_wallets — Ví tài khoản ký quỹ của người dùng & người bán."""
    __tablename__ = "escrow_wallets"

    id = Column(String(36), primary_key=True, default=lambda: f"wal-{uuid.uuid4().hex[:8]}")
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    available_balance = Column(BigInteger, default=0, nullable=False)  # Số dư khả dụng có thể rút (VND)
    locked_balance = Column(BigInteger, default=0, nullable=False)     # Số tiền đang tạm giữ trong các đơn hàng mở
    total_withdrawn = Column(BigInteger, default=0, nullable=False)    # Lũy kế số tiền đã rút về ngân hàng
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="wallet")
    transactions = relationship("EscrowTransaction", back_populates="wallet", cascade="all, delete-orphan", order_by="EscrowTransaction.created_at.desc()")

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "availableBalance": self.available_balance,
            "lockedBalance": self.locked_balance,
            "totalTvl": self.available_balance + self.locked_balance,
            "totalWithdrawn": self.total_withdrawn,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class EscrowTransaction(Base):
    """Bảng 17: escrow_transactions — Sổ cái biến động số dư ký quỹ."""
    __tablename__ = "escrow_transactions"

    id = Column(String(36), primary_key=True, default=lambda: f"tx-{uuid.uuid4().hex[:8]}")
    wallet_id = Column(String(36), ForeignKey("escrow_wallets.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    transaction_code = Column(String(40), unique=True, index=True, nullable=False)  # TX-ESC-2026-XXXX
    transaction_type = Column(String(20), nullable=False)  # 'deposit', 'hold_order', 'release_payout', 'refund_buyer', 'withdrawal'
    amount = Column(BigInteger, nullable=False)  # (+/-)
    balance_after = Column(BigInteger, nullable=False)
    memo = Column(Text, nullable=False)
    bank_reference_code = Column(String(50), default="")
    status = Column(String(20), default="completed", nullable=False)  # 'pending', 'completed', 'failed'
    created_at = Column(DateTime, default=func.now(), nullable=False)

    wallet = relationship("EscrowWallet", back_populates="transactions")
    order = relationship("Order")

    def to_dict(self):
        return {
            "id": self.id,
            "walletId": self.wallet_id,
            "orderId": self.order_id,
            "transactionCode": self.transaction_code,
            "transactionType": self.transaction_type,
            "amount": self.amount,
            "balanceAfter": self.balance_after,
            "memo": self.memo,
            "bankReferenceCode": self.bank_reference_code,
            "status": self.status,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
