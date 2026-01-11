from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

# Enum untuk Prioritas Pengeluaran (The 3 Buckets)
class PriorityGroup(str, enum.Enum):
    FIXED = "fixed"      # Kewajiban (KPR, Listrik)
    LIVING = "living"    # Kebutuhan (Makan, Transport)
    LIFESTYLE = "lifestyle" # Keinginan (Hobi, Kopi)
    INCOME = "income"    # Pemasukan

# Enum untuk Tipe Transaksi
class TransactionType(str, enum.Enum):
    EXPENSE = "expense"
    INCOME = "income"
    TRANSFER = "transfer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    pin_hash = Column(String) # Untuk keamanan sederhana

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # Cash, BCA, Gopay
    wallet_type = Column(String) # Bank, E-Wallet, Cash
    initial_balance = Column(Float, default=0.0)
    is_active = Column(Integer, default=1) # 1=Active, 0=Archived (Soft Delete)
    
    transactions = relationship("Transaction", back_populates="wallet")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # Makanan, Listrik, Gaji
    category_type = Column(Enum(TransactionType)) # expense, income
    priority_group = Column(Enum(PriorityGroup), nullable=True) # Fixed, Living, Lifestyle (Only for expenses)
    icon = Column(String, nullable=True) # Phosphor icon name (e.g., "coffee")

    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    amount = Column(Float)
    description = Column(String, nullable=True)
    receipt_path = Column(String, nullable=True) # Path to image
    
    wallet_id = Column(Integer, ForeignKey("wallets.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    wallet = relationship("Wallet", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    amount_limit = Column(Float)
    month_period = Column(String) # Format "YYYY-MM"
    
    category = relationship("Category", back_populates="budgets")

class AIAdvice(Base):
    __tablename__ = "ai_advice"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String) # Isi nasihat
    created_at = Column(DateTime(timezone=True), server_default=func.now())
