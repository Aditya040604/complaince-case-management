from sqlalchemy.orm import Session
from app.models.audit_logs import AuditLog


def create_audit_log(
        db: Session,
        action: str,
        entity_type: str,
        entity_id: int | None = None,
        old_value: str | None = None,
        new_value: str | None = None,

        case_id: int | None = None,
        user_id: int | None = None, 
):
    audit_log = AuditLog(
        user_id=user_id,
        case_id= case_id,
        action = action,
        entity_id = entity_id,
        entity_type = entity_type,
        old_value = old_value,
        new_value = new_value
    )

    db.add(audit_log)
    