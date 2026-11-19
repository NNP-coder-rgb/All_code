"""
escrow.py — Router xử lý Ví Ký Quỹ Escrow & Sổ Cái 24/7
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.escrow import EscrowWallet, EscrowTransaction


def handle_get_wallet(db: Session, user_id: str) -> Dict[str, Any]:
    wallet = db.query(EscrowWallet).filter(EscrowWallet.user_id == user_id).first()
    if not wallet:
        return {
            "success": True,
            "message": "Người dùng chưa có ví ký quỹ",
            "data": {
                "availableBalance": 0,
                "lockedBalance": 0,
                "totalTvl": 0,
                "totalWithdrawn": 0,
                "transactions": []
            },
            "status_code": 200
        }
    res = wallet.to_dict()
    res["transactions"] = [tx.to_dict() for tx in wallet.transactions]
    return {"success": True, "message": "Lấy thông tin ví thành công", "data": res, "status_code": 200}
