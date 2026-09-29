from typing import Any

from gsuid_core.logger import logger


async def _ensure_tables() -> None:
    from gsuid_core.utils.database.startup import ensure_core_database_tables

    await ensure_core_database_tables()


def get_sqla(bot_id: Any = None) -> None:
    logger.debug(f"Pokemon: get_sqla({bot_id!r})")
    return None


__all__ = ["get_sqla"]
