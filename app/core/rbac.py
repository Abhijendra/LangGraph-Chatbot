from enum import Enum

from app.core.auth import UserContext, Role

ADMIN_TITLES = {"President", "Administrative Vice President"}
HR_TITLES = {"Human Resources Representative"}

def role_from_job_title(job_title:str | None) -> Role:

    if job_title in ADMIN_TITLES:
        return Role.ADMIN

    if job_title in HR_TITLES:
        return Role.HR

    return Role.EMPLOYEE   #default

class Permission(str, Enum):
    EMPLOYEE_READ_BASIC = "employee:read_basic"
    EMPLOYEE_READ_OWN_DETAILS = "employee:read_own_details"
    EMPLOYEE_READ_ANY_DETAILS = "employee:read_any_details"
    DEPARTMENT_READ = "department:read"
    FINANCE_READ = "finance:read"
    WEB_SEARCH = "web:search"

_EMPLOYEE_PERMS = {
    Permission.EMPLOYEE_READ_BASIC,
    Permission.EMPLOYEE_READ_OWN_DETAILS,
    Permission.DEPARTMENT_READ,
    Permission.FINANCE_READ,
    Permission.WEB_SEARCH
}

_HR_PERMS = {
    Permission.EMPLOYEE_READ_OWN_DETAILS,
    Permission.EMPLOYEE_READ_ANY_DETAILS,
    Permission.DEPARTMENT_READ,
    Permission.WEB_SEARCH,
    Permission.EMPLOYEE_READ_BASIC
}

# HR: employee permissions plus access to anyone's details
_ADMIN_PERMS = _EMPLOYEE_PERMS | {Permission.EMPLOYEE_READ_ANY_DETAILS}

# Assigning (Mapping) permissions to roles
ROLE_PERMISSIONS: dict[Role:set[Permission]] = {
    Role.EMPLOYEE: _EMPLOYEE_PERMS,
    Role.HR: _HR_PERMS,
    Role.ADMIN: _ADMIN_PERMS
}

class PermissionDenied(Exception):
    """Raised when a user tries to do something their role does not allow"""

def has_permission(user:UserContext, perm: Permission) -> bool:
    permissions = ROLE_PERMISSIONS.get(user.role, set())
    if perm in permissions:
        return True
    return False


def require(user:UserContext, perm:Permission) -> None:
    if not has_permission(user, perm):
        raise PermissionDenied("You don't have permission to access this info.")