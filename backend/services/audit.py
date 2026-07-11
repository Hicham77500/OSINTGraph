"""Audit service helpers."""
from db.domain_client import domain_client


async def record(actor: str, action: str, entity_type: str, entity_id: str, prev=None, new=None):
    await domain_client.record_audit(actor, action, entity_type, entity_id, prev, new)
