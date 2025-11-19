from pymongo import MongoClient
from app.core.config import settings


def get_db():
    """
    Return (client, db). Caller should keep client for proper shutdown:
      client, db = get_db()
    """
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.DATABASE_NAME]
    return client, db