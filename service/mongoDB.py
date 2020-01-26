import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.environ.get("MONGO_URI") or "mongodb://username:secret@localhost:27017/?authSource=admin"

async def db_setup():
    # client = AsyncIOMotorClient(MONGODB_HOST, MONGODB_PORT)
    mongo_uri = MONGO_URI
    client = AsyncIOMotorClient(mongo_uri)
    atlas = client['atlas']
    plat = atlas['plat']
    return plat
