from sqlalchemy import select, func
from app.db.engine import SessionLocal
from app.db.models import Employee
from app.core.auth import UserContext

async def get_by_name(user: UserContext, name: str, last_name: str|None=None) -> list[dict]:
    """Find employees by first name, and optionally last name. Returns at most 5 rows."""
    
    # TODO(RBAC)

    async with SessionLocal() as session:
        stmt = select(Employee.employee_id, 
                      Employee.first_name, 
                      Employee.last_name, 
                      Employee.department_id).where( 
                          func.lower(Employee.first_name) == name.lower()
                          ).limit(5)

        if last_name:
            stmt = stmt.where(func.lower(Employee.last_name) == last_name.lower()).limit(5)
        
        result = await session.execute(stmt)
        return [dict(row) for row in result.mappings().all()]
