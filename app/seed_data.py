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
        "cases:assign",
        "audit:read",
        "users:manage"
    ],

    "Manager": [
        "cases:read",
        "cases:create",
        "cases:update",
        "cases:close",
        "cases:assign",
        "audit:read",
    ],
    "Analyst": [
        "cases:read",
        "cases:create",
        "cases:update",
        "cases:close",
        "cases:self_assign",
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
    "cases:self_assign",
    "cases:assign",
    "audit:read",
    "users:manage"
]

db = SessionLocal()




try:
    # 1. Inserting missing roles
    for role_name in roles:
        db.execute(
            insert(Role)
            .values(
                name=role_name
            )
            .on_conflict_do_nothing(index_elements=["name"])
        )
    # 2. Insert missing permissions
    for permission_name in permissions:
        db.execute(
            insert(Permission)
            .values(
                name=permission_name
            )
            .on_conflict_do_nothing(index_elements=["name"])
        )


    obsolete_permissions = ["cases:reopen"]

    for permission_name in obsolete_permissions:
        obsolete_permission = db.scalar(
            select(Permission).where(Permission.name == permission_name)
        )
        if obsolete_permission:
            db.execute(
                role_permissions.delete().where(
                    role_permissions.c.permission_id == obsolete_permission.id
                )
            )
            db.delete(obsolete_permission)



    for role_name, permission_names in role_permission_map.items():
        role = db.scalar(
            select(Role).where(Role.name == role_name)
        )
        for permission_name in permission_names:
            permission = db.scalar(
                select(Permission).where(Permission.name == permission_name)
            )
            db.execute( insert(role_permissions).values(role_id = role.id, permission_id = permission.id).on_conflict_do_nothing(index_elements=["role_id", "permission_id"]))
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
