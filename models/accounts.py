from models.base import Base
from sqlalchemy import Integer, String, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func

from flask_login import UserMixin


class Accounts(Base, UserMixin):
    __tablename__ = 'accounts'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(Integer, ForeignKey('user.id'))
    account_type = mapped_column(String(255), nullable=False)
    account_number = mapped_column(String(255), nullable=False)
    balance = mapped_column(DECIMAL(10, 2), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='accounts')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_type': self.account_type,
            'account_number': self.account_number,
            'balance': str(self.balance),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __repr__(self):
        return f'<Accounts {self.account_number}>'