"""
Example: Use SQLAdapter with SQLite to persist data.

This script demonstrates creating a SQLite file, inserting a row, and querying it using
the Repository + SQLAdapter. It uses asyncio to run the async adapter operations.
"""

import asyncio

from guaro import API, DatabaseEngine, Model
from guaro.core.query_ir import QueryIR
from guaro.db.adapters.sql_adapter import SQLAdapter
from guaro.db.repository import Repository


class User(Model):
    id: int
    name: str


async def main():
    api = API(database={"url": "sqlite+aiosqlite:///guaro_test.db", "engine": DatabaseEngine.SQLITE})
    api.register_model(User)
    # create adapter (registry now has model metadata)
    adapter = SQLAdapter(api.registry, api.db_config.url)
    await adapter.connect()

    repo = Repository(adapter)

    # remove existing id if present (idempotent for repeated runs)
    from guaro.core.query_ir import QueryIR

    ir_del = QueryIR(entity="User")
    ir_del.add_filter("id", "==", 1)
    await adapter.delete(ir_del)

    # insert a row
    created = await adapter.insert("User", {"id": 1, "name": "Ali"})
    print("Created:", created.__dict__ if hasattr(created, "__dict__") else created)

    # query
    ir = QueryIR(entity="User", fields=["id", "name"]) 
    rows = await repo.find(ir)
    print("Rows:", [r.__dict__ for r in rows])

    await adapter.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
