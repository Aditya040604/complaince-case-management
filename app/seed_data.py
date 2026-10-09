from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.database import SessionLocal
from app.models import Role, Permission, role_permissions

role_permission_map = {
    "Admin": [
        "cases:read",
        "cases:create",
        "cases:update",
        "cases:close",
        "cases:reopen",
        "cases:assign",
        "audit:read",
        "users:manage"
    ],

    "Manager": [
        "cases:read",
        "cases:create",
        "cases:update",
        "cases:close",
        "cases:reopen",
        "cases:assign",
        "audit:read",
    ],
    "Analyst": [
        "cases:read",
        "cases:create",
        "cases:update",
        "audit:read",
    ],
    "Viewer": [
        "cases:read"
    ]
}

roles = [
    "Admin",
    "Manager",
    "Analyst",
    "Viewer",
]

permissions = [
    "cases:read",
    "cases:create",
    "cases:update",
    "cases:close",
    "cases:reopen",
    "cases:assign",
    "audit:read",
    "users:manage"
]

db = SessionLocal()


try:
    for role_name, permission_names in role_permission_map.items():
        role = db.scalar(
            select(Role).where(Role.name == role_name)

        )
        for permission_name in permission_names:
            permission = db.scalar(
                select(Permission).where(Permission.name == permission_name)
            )
            db.execute( insert(role_permissions).values(role_id = role.id, permission_id = permission.id).on_conflict_do_nothing())
    db.commit()



finally:
    db.close()

# try:
#     for role_name in roles:
#         existing_role = db.scalar(
#             select(Role).where(Role.name == role_name)
#         )

#         if existing_role is None:
#             db.add(Role(name = role_name))
#     for permission_name in permissions:
#         existing_permission = db.scalar(
#             select(Permission).where(Permission.name == permission_name)

#         )
#         if existing_permission is None:
#             db.add(Permission(name = permission_name))
#     db.commit()

# finally:
#     db.close()
