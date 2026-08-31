from models.users import UserRole


ROLE_HIERARCHY = {
    UserRole.EMPLOYEE: 0,
    UserRole.TECHNICIAN: 1,
    UserRole.SUPERUSER: 2
}
