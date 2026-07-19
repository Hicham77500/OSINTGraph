"""
OSINTGraph — Centralized API Manager
"""
import os
import logging
from typing import Dict, Any, Optional
import aiosqlite

logger = logging.getLogger("osintgraph.api_manager")

def _db_path() -> str:
    return os.getenv("SQLITE_PATH", "osintgraph.db")

class ApiManager:
    """Manages API keys from environment variables and tracks usage/quotas in DB."""
    
    async def _connect(self) -> aiosqlite.Connection:
        db = await aiosqlite.connect(_db_path())
        await db.execute("PRAGMA journal_mode=WAL")
        return db
        
    def get_env_key(self, provider_name: str) -> Optional[str]:
        """Get API key from environment (.env). e.g., 'shodan' -> 'SHODAN_API_KEY'"""
        env_var_name = f"{provider_name.upper()}_API_KEY"
        return os.getenv(env_var_name)

    async def get_provider(self, provider_name: str) -> Dict[str, Any]:
        """Fetch provider status from DB."""
        async with await self._connect() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM api_providers WHERE name = ?", (provider_name,)) as cur:
                row = await cur.fetchone()
        
        if row:
            return dict(row)
        return {
            "name": provider_name,
            "status": "ACTIVE",
            "daily_limit": -1,
            "remaining_quota": -1,
            "last_used": None
        }

    async def get_key_and_check_quota(self, provider_name: str) -> Optional[str]:
        """
        Returns the API key if available and quota allows it.
        Otherwise returns None.
        """
        key = self.get_env_key(provider_name)
        if not key:
            return None
            
        provider = await self.get_provider(provider_name)
        if provider["status"] != "ACTIVE":
            logger.warning(f"Provider {provider_name} is disabled.")
            return None
            
        if provider["daily_limit"] > 0 and provider["remaining_quota"] == 0:
            logger.warning(f"Provider {provider_name} quota exceeded.")
            return None
            
        return key

    async def register_usage(self, provider_name: str, cost: int = 1):
        """Update last_used and decrement quota if applicable."""
        async with await self._connect() as db:
            async with db.execute("SELECT remaining_quota FROM api_providers WHERE name = ?", (provider_name,)) as cur:
                row = await cur.fetchone()
                
            if not row:
                # Insert tracking row
                await db.execute(
                    "INSERT INTO api_providers (id, name, last_used) VALUES (lower(hex(randomblob(16))), ?, datetime('now'))",
                    (provider_name,)
                )
            else:
                remaining = row[0]
                if remaining > 0:
                    new_remaining = max(0, remaining - cost)
                    await db.execute(
                        "UPDATE api_providers SET last_used = datetime('now'), remaining_quota = ? WHERE name = ?",
                        (new_remaining, provider_name)
                    )
                else:
                    await db.execute(
                        "UPDATE api_providers SET last_used = datetime('now') WHERE name = ?",
                        (provider_name,)
                    )
            await db.commit()

api_manager = ApiManager()
