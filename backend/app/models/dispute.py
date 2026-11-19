"""
models/dispute.py — Models SQLAlchemy cho Phòng Trọng Tài Tranh Chấp 3 Bên, Bằng Chứng & Chat Đối Soát
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Dispute(Base):
    """Bảng 18: disputes — Hồ sơ vụ việc khiếu nại tranh chấp 3 bên."""
    __tablename__ = "disputes"

    id = Column(String(36), primary_key=True, default=lambda: f"dsp-{uuid.uuid4().hex[:8]}")
    dispute_code = Column(String(30), unique=True, index=True, nullable=False)  # DSP-2026-001
    order_id = Column(String(36), ForeignKey("orders.id"), unique=True, nullable=False, index=True)
    buyer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    seller_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    reason = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    requested_refund = Column(BigInteger, nullable=False)
    approved_refund = Column(BigInteger, default=0, nullable=False)
    status = Column(String(30), default="pending", nullable=False, index=True)  # 'pending', 'seller_responded', 'in_arbitration', 'resolved', 'closed'
    arbitrator_admin_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    admin_decision_summary = Column(Text, default="")
    solution_code = Column(String(30), default="")  # 'full_refund', 'partial_refund', 'reject_claim'
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    order = relationship("Order", back_populates="dispute")
    buyer = relationship("User", foreign_keys=[buyer_id])
    seller = relationship("User", foreign_keys=[seller_id])
    arbitrator = relationship("User", foreign_keys=[arbitrator_admin_id])
    evidences = relationship("DisputeEvidence", back_populates="dispute", cascade="all, delete-orphan")
    messages = relationship("DisputeMessage", back_populates="dispute", cascade="all, delete-orphan", order_by="DisputeMessage.created_at")

    def to_dict(self):
        return {
            "id": self.id,
            "disputeCode": self.dispute_code,
            "orderId": self.order_id,
            "orderCode": self.order.order_code if self.order else None,
            "buyerId": self.buyer_id,
            "buyerName": self.buyer.full_name if self.buyer else None,
            "sellerId": self.seller_id,
            "sellerName": self.seller.full_name if self.seller else None,
            "reason": self.reason,
            "description": self.description,
            "requestedRefund": self.requested_refund,
            "approvedRefund": self.approved_refund,
            "status": self.status,
            "adminDecisionSummary": self.admin_decision_summary,
            "solutionCode": self.solution_code,
            "evidences": [ev.to_dict() for ev in self.evidences] if self.evidences else [],
            "messages": [msg.to_dict() for msg in self.messages] if self.messages else [],
            "resolvedAt": self.resolved_at.isoformat() if self.resolved_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class DisputeEvidence(Base):
    """Bảng 19: dispute_evidences — Bằng chứng ảnh, video mở hộp đồng kiểm."""
    __tablename__ = "dispute_evidences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dispute_id = Column(String(36), ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    media_url = Column(Text, nullable=False)
    media_type = Column(String(20), default="image", nullable=False)  # 'image' | 'video' | 'pdf'
    title = Column(String(150), nullable=False)
    file_size_kb = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    dispute = relationship("Dispute", back_populates="evidences")
    uploader = relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "disputeId": self.dispute_id,
            "uploadedByUserId": self.uploaded_by_user_id,
            "mediaUrl": self.media_url,
            "mediaType": self.media_type,
            "title": self.title,
            "fileSizeKb": self.file_size_kb,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class DisputeMessage(Base):
    """Bảng 20: dispute_messages — Nhật ký chat đối thoại 3 bên trong phòng khiếu nại."""
    __tablename__ = "dispute_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dispute_id = Column(String(36), ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    sender_role = Column(String(20), nullable=False)  # 'buyer', 'seller', 'admin', 'system'
    message_text = Column(Text, nullable=False)
    attachment_url = Column(Text, default="")
    created_at = Column(DateTime, default=func.now(), nullable=False)

    dispute = relationship("Dispute", back_populates="messages")
    sender = relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "disputeId": self.dispute_id,
            "senderId": self.sender_id,
            "senderRole": self.sender_role,
            "senderName": self.sender.full_name if self.sender else "Hệ thống",
            "messageText": self.message_text,
            "text": self.message_text,
            "attachmentUrl": self.attachment_url,
            "time": self.created_at.strftime("%H:%M") if self.created_at else "",
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
