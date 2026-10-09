# Many to many junction table

from sqlalchemy import Table, Column, ForeignKey

from app.database import Base

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),


)

#The two columns together prevent duplicate role-permission assignments.