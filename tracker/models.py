from tracker.common import get_time
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Sequence, Boolean, Numeric
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, Sequence("users_id_seq"), primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String(13))
    hash = Column(String, nullable=False)


class Merchant(Base):
    __tablename__ = "merchant"
    id = Column(Integer, Sequence("merchant_id_seq"), primary_key=True)
    name = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)


class UserTransaction(Base):
    __tablename__ = "user_transactions"

    id = Column(Integer, Sequence("user_transactions_id_seq"), primary_key=True)
    creditor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    debitor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    txn_amount = Column(Numeric, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=get_time())
    updated_at = Column(TIMESTAMP, nullable=False, default=get_time())
    description = Column(String)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=True)


class Expenses(Base):
    __tablename__ = "expenses"

    id = Column(Integer, Sequence("expenses_id_seq"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    txn_amount = Column(Numeric, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchant.id"), nullable=False)
    description = Column(String)


class ExpenseParties(Base):
    __tablename__ = "expense_parties"

    id = Column(Integer, Sequence("expense_parties_id_seq"), primary_key=True)
    amount = Column(Numeric, nullable=False)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class Groups(Base):

    __tablename__ = "groups"

    id = Column(Integer, Sequence("groups_id_seq"), primary_key=True)
    name = Column(String(100), nullable=False)


class UserGroupMapping(Base):

    __tablename__ = "user_group_mapping"

    id = Column(Integer, Sequence("user_group_mapping_id_seq"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class Friends(Base):

    __tablename__ = "friends"

    id = Column(Integer, Sequence("friends_id_seq"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.id"), nullable=False)


# balance
# expenses
