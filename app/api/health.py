from fastapi import APIRouter, Depends
from pymongo.database import Database
from pymongo.errors import PyMongoError

from app.db.mongo import get_database

router = APIRouter()


@router.get("/health")
def health(db: Database = Depends(get_database)) -> dict:
    try:
        db.command("ping")
        mongo_status = "ok"
    except PyMongoError:
        mongo_status = "unreachable"

    return {"status": "ok", "mongo": mongo_status}
