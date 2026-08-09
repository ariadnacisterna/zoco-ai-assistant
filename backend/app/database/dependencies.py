from fastapi import Request

from app.database.mongodb import MongoDatabase


def get_mongo_database(request: Request) -> MongoDatabase:
    """Return the MongoDB instance stored in the application state."""

    return request.app.state.mongo_database
