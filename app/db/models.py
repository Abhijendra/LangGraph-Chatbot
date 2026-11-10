from datetime import date
from decimal import Decimal

from sqlalchemy import CHAR, Date, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Region(Base):
    __tablename__ = "regions"
    __table_args__ = {"schema": "hr"}

    region_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    region_name: Mapped[str | None] = mapped_column(String(25))

    def __repr__(self) -> str:
        return f"Region(region_id={self.region_id!r}, region_name={self.region_name!r})"


class Country(Base):
    __tablename__ = "countries"
    __table_args__ = {"schema": "hr"}

    country_id: Mapped[str] = mapped_column(CHAR(2), primary_key=True)
    country_name: Mapped[str | None] = mapped_column(String(40))
    region_id: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"Country(country_id={self.country_id!r}, country_name={self.country_name!r})"


class Location(Base):
    __tablename__ = "locations"
    __table_args__ = {"schema": "hr"}

    location_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    street_address: Mapped[str | None] = mapped_column(String(40))
    postal_code: Mapped[str | None] = mapped_column(String(12))
    city: Mapped[str] = mapped_column(String(30))
    state_province: Mapped[str | None] = mapped_column(String(25))
    country_id: Mapped[str] = mapped_column(CHAR(2))

    def __repr__(self) -> str:
        return f"Location(location_id={self.location_id!r}, city={self.city!r})"


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = {"schema": "hr"}

    department_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_name: Mapped[str] = mapped_column(String(30))
    manager_id: Mapped[int | None] = mapped_column(Integer)
    location_id: Mapped[int | None] = mapped_column(Integer)

    def __repr__(self) -> str:
        return (
            f"Department(department_id={self.department_id!r}, "
            f"department_name={self.department_name!r})"
        )


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = {"schema": "hr"}

    job_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    job_title: Mapped[str] = mapped_column(String(35))
    min_salary: Mapped[Decimal | None] = mapped_column(Numeric(8, 0))
    max_salary: Mapped[Decimal | None] = mapped_column(Numeric(8, 0))

    def __repr__(self) -> str:
        return f"Job(job_id={self.job_id!r}, job_title={self.job_title!r})"


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = {"schema": "hr"}

    employee_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String(20))
    last_name: Mapped[str] = mapped_column(String(25))
    email: Mapped[str] = mapped_column(String(25))
    phone_number: Mapped[str | None] = mapped_column(String(20))
    hire_date: Mapped[date] = mapped_column(Date)
    job_id: Mapped[str] = mapped_column(String(10))
    salary: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    commission_pct: Mapped[Decimal | None] = mapped_column(Numeric(2, 2))
    manager_id: Mapped[int | None] = mapped_column(Integer)
    department_id: Mapped[int | None] = mapped_column(Integer)

    # Salary, email and phone are left out on purpose: keep sensitive data out of logs.
    def __repr__(self) -> str:
        return (
            f"Employee(employee_id={self.employee_id!r}, "
            f"name={self.first_name!r} {self.last_name!r})"
        )


class JobHistory(Base):
    __tablename__ = "job_history"
    __table_args__ = {"schema": "hr"}

    # The table has no primary key, only UNIQUE (employee_id, start_date).
    # SQLAlchemy needs a key, so we declare that pair as the primary key here.
    employee_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_date: Mapped[date] = mapped_column(Date, primary_key=True)
    end_date: Mapped[date] = mapped_column(Date)
    job_id: Mapped[str] = mapped_column(String(10))
    department_id: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return (
            f"JobHistory(employee_id={self.employee_id!r}, "
            f"start_date={self.start_date!r}, job_id={self.job_id!r})"
        )
