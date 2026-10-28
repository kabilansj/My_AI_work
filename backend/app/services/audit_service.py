"""Centralized audit logging service."""

import json
from typing import Any, Optional
from sqlalchemy.orm import Session
from ..models.audit import AuditLog


class AuditService:
    """Manages immutable audit log entries for all human and automated actions."""

    @staticmethod
    def log(
        db: Session,
        document_id: str,
        entity_type: str,
        entity_id: str,
        action: str,
        prior_state: Optional[Any] = None,
        new_state: Optional[Any] = None,
        user_id: str = "clinician_user",
        reason: Optional[str] = None,
    ) -> AuditLog:
        """Create and commit an audit log event."""
        log_entry = AuditLog(
            document_id=document_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            prior_state=json.dumps(prior_state) if prior_state is not None else None,
            new_state=json.dumps(new_state) if new_state is not None else None,
            user_id=user_id,
            reason=reason,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
