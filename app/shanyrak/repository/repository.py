from datetime import datetime

from bson.objectid import ObjectId
from pymongo.database import Database


class ShanyrakRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_ad(self, ad: dict, user_id: str):
        ad["user_id"] = user_id
        ad["created_at"] = datetime.utcnow()

        result = self.database["ads"].insert_one(ad)

        return result.inserted_id

    def get_ad_by_id(self, ad_id: str) -> dict | None:
        ad = self.database["ads"].find_one(
            {
                "_id": ObjectId(ad_id),
            }
        )
        return ad

    def update_ad(self, ad_id: str, data: dict):
        self.database["ads"].update_one(
            filter={"_id": ObjectId(ad_id)},
            update={
                "$set": {
                    "type": data["type"],
                    "price": data["price"],
                    "address": data["address"],
                    "area": data["area"],
                    "rooms_count": data["rooms_count"],
                    "description": data["description"],
                }
            },
        )

    def delete_ad(self, ad_id: str):
        self.database["ads"].delete_one(
            {
                "_id": ObjectId(ad_id),
            }
        )
