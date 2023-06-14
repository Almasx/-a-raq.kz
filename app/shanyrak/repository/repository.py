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

    def post_media(self, ad_id: str, data: list[str]):
        self.database["ads"].update_one(
            filter={"_id": ObjectId(ad_id)},
            update={"$set": {"media": data}},
        )

    def delete_media(self, ad_id: str, data: list[str]):
        self.database["ads"].update_one(
            filter={"_id": ObjectId(ad_id)},
            update={"$pull": {"media": {"$in": data}}},
        )

    def add_comment(self, ad_id: str, comment_content: str, user_id: str):
        comment = {
            "_id": str(ObjectId()),
            "content": comment_content,
            "created_at": datetime.utcnow(),
            "author_id": user_id,
        }

        self.database["ads"].update_one(
            {"_id": ObjectId(ad_id)}, {"$push": {"comments": comment}}
        )

    def get_comments_by_ad_id(self, ad_id: str) -> list[dict] | None:
        ad = self.database["ads"].find_one(
            {"_id": ObjectId(ad_id)}, {"comments": 1, "_id": 0}
        )
        return ad["comments"] if ad and "comments" in ad else None

    def update_comment(
        self, ad_id: str, comment_id: str, comment_content: str, user_id: str
    ):
        self.database["ads"].update_one(
            {
                "_id": ObjectId(ad_id),
                "comments._id": comment_id,
                "comments.author_id": user_id,
            },
            {"$set": {"comments.$.content": comment_content}},
        )

    def delete_comment(self, ad_id: str, comment_id: str, user_id: str):
        self.database["ads"].update_one(
            {"_id": ObjectId(ad_id)},
            {"$pull": {"comments": {"_id": comment_id, "author_id": user_id}}},
        )
