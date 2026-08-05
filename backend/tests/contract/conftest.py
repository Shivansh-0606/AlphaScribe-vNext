"""Hermetic import shim for the contract suite.

`import server` at module scope reads MONGO_URL/DB_NAME (server.py:42-43) and
constructs an AsyncIOMotorClient — but motor/pymongo clients connect lazily,
so this succeeds with no reachable Mongo and no network call, which is what
makes app.openapi() callable without a running server (06 §5.1 Ph0; the
app-factory refactor that removes this need entirely lands in Ph1, 06 AD-1).
"""
import os

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_contract_test")
