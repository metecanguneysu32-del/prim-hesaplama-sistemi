from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    username: str
    password: str
    full_name: str
    active: bool = True


@dataclass
class Store:
    store_code: str
    store_name: str
    city: str = ""
    district: str = ""
    region: str = ""
    is_istanbul: bool = False
    active: bool = True


@dataclass
class Personnel:
    personnel_code: str
    full_name: str
    title: str
    store_code: str
    active: bool = True


@dataclass
class WeeklyTarget:
    year: int
    week: int
    store_code: str
    target_amount: float


@dataclass
class Sale:
    year: int
    week: int
    store_code: str
    personnel_code: str
    sale_amount: float


@dataclass
class CorporateSale:
    year: int
    week: int
    store_code: str
    personnel_code: str
    amount: float
    description: str = ""


@dataclass
class InStoreSale:
    year: int
    week: int
    store_code: str
    personnel_code: str
    amount: float
    description: str = ""


@dataclass
class CommissionRate:
    city_type: str
    min_rate: float
    max_rate: float
    title: str
    amount_per_2500: float


@dataclass
class CommissionResult:
    year: int
    week: int
    personnel_code: str
    store_code: str
    sale_amount: float
    corporate_sale: float
    instore_sale: float
    total_sale: float
    target_rate: float
    commission_amount: float


@dataclass
class ImportLog:
    file_type: str
    file_name: str
    import_date: str
    total_rows: int
    success_rows: int
    error_rows: int


@dataclass
class SalesSummary:
    personnel_code: str
    store_code: str
    personnel_name: str
    title: str
    sale_amount: float
    corporate_sale: float
    instore_sale: float
    total_sale: float


@dataclass
class ImportResult:
    file_type: str
    file_name: str
    total_rows: int
    success_rows: int
    error_rows: int
    errors: Optional[list] = None