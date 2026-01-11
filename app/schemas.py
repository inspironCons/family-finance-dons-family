from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from .models import TransactionType, PriorityGroup

class WalletBase(BaseModel):
    name: str
    wallet_type: str
    initial_balance: float

class WalletCreate(WalletBase):
    pass

class Wallet(WalletBase):
    id: int
    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    category_type: TransactionType
    priority_group: Optional[PriorityGroup] = None
    icon: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    date: date
    amount: float
    description: Optional[str] = None
    wallet_id: int
    category_id: int

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    class Config:
        from_attributes = True
