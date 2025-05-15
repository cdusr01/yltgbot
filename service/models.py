from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Role:
    __tablename__ = "roles"
    id: int
    type: str
    rate: Decimal


@dataclass
class User:
    __tablename__ = "users"
    id: int
    user_id: str
    user_tag: str
    role_id: int
    balance: float


@dataclass
class Freelancer:
    __tablename__ = "freelancers"
    id: int
    user_id: User
    login: str
    passwd: str
    amount: int
    salary: float


@dataclass
class Subject:
    __tablename__ = "subjects"
    id: int
    name: str


@dataclass
class OrderType:
    __tablename__ = "order_types"
    id: int
    name: str
    price: int
    deadline: int
    subject_id: int


@dataclass
class Status:
    __tablename__ = "statuses"
    id: int
    state: str


@dataclass
class Order:
    __tablename__ = "orders"
    id: int
    user_id: int
    subject_id: int
    order_type_id: int
    order_text: str
    is_urgent: bool
    status_id: int
    freelancer_id: int = None
    created_at: str = None
    deadline: str = None
    completed_at: str = None
