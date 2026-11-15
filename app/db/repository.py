from sqlalchemy import select, func
from app.db.engine import SessionLocal
from app.db.models import Employee, Department, Job
from app.core.auth import UserContext
from app.core.rbac import require, Permission

async def get_by_name(user: UserContext, name: str, last_name: str|None=None) -> list[dict]:
    """Find employees by first name, and optionally last name. Returns at most 5 rows."""
    
    # RBAC
    require(user, Permission.EMPLOYEE_READ_BASIC)

    async with SessionLocal() as session:
        stmt = select(Employee.employee_id, 
                      Employee.first_name, 
                      Employee.last_name, 
                      Employee.job_id,
                      Employee.department_id).where( 
                          func.lower(Employee.first_name) == name.lower()
                          ).limit(5)

        if last_name:
            stmt = stmt.where(func.lower(Employee.last_name) == last_name.lower()).limit(5)
        
        result = await session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]

async def get_department_by_id(user: UserContext, dept_id: int):
    """
    Fetches all the detail of department by department id.
    """

    # RBAC
    require(user, Permission.DEPARTMENT_READ)

    async with SessionLocal() as session:
        stmt = select(
            Department.department_name,
            Department.department_id,
            Department.manager_id,
            Department.location_id
            ).where(
            Department.department_id == dept_id
        )

        result = await session.execute(stmt)
        department = result.mappings().all()
        return department

async def get_login_info(employee_id:int) -> dict | None:
    """Returns {employee_id, job_title} or None if the employee does not exist."""
    async with SessionLocal() as session:

        stmt = (
            select (Employee.employee_id, Job.job_title)
            .join(Job, Job.job_id == Employee.job_id)
            .where(Employee.employee_id == employee_id)
        )
        result = await session.execute(stmt)
        row = result.mappings().first()
        return dict(row) if row else None


async def get_employee_details(user: UserContext, employee_id: int):
    """Full profile: includes salary, email, phone."""

    # RBAC
    if str(employee_id) == user.user_id:
        require(user, Permission.EMPLOYEE_READ_OWN_DETAILS)
    else:
        require(user, Permission.EMPLOYEE_READ_ANY_DETAILS)

    async with SessionLocal() as session:

        stmt = select(
            Employee.employee_id, Employee.first_name, Employee.last_name,
            Employee.email, Employee.phone_number, Employee.hire_date,
            Employee.salary, Employee.commission_pct,
            Employee.job_id, Employee.manager_id, Employee.department_id,
        ).where(Employee.employee_id == employee_id)

        result = await session.execute(stmt)
        return [dict(r) for r in result.mappings().all()]
