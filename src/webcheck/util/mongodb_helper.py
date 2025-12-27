from typing import List

from pymongo import MongoClient, DESCENDING

from webcheck import conf

mongo: MongoClient | None = None

def get_global_mongo_client() -> MongoClient:
    global mongo
    if mongo is None:
        mongo = get_mongo_client()
    return mongo


def get_mongo_client(ping: bool = False) -> MongoClient:
    mongodb_uri = conf.MONGODB_URI
    if not mongodb_uri:
        raise ValueError("MONGODB_URI is not set in environment variables.")

    client = MongoClient(mongodb_uri)
    if ping:
        try:
            # The ismaster command is cheap and does not require auth.
            client.admin.command('ismaster')
        except Exception as e:
            raise ConnectionError(f"Could not connect to MongoDB: {e}")
    return client


def get_mongo_collection(db_name: str, collection_name: str):
    _mongo = get_mongo_client()
    return _mongo[db_name][collection_name]


def mongodb_results_to_json(results: List[dict], strip_id=True) -> List[dict]:
    json_results = []
    for doc in results:
        if strip_id and "_id" in doc:
            doc.pop("_id")
        elif "_id" in doc:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
        json_results.append(doc)
    return json_results


def mongodb_result_to_json(result: dict, strip_id=True) -> dict:
    if result and "_id" in result:
        if strip_id and "_id" in result:
            result.pop("_id")
        elif "_id" in result:
            result["_id"] = str(result["_id"])  # Convert ObjectId to string
    return result


def mongodb_upsert_domain_scan(domain_name: str, scan_data: dict) -> None:
    collection = get_mongo_collection(conf.MONGODB_DB_NAME, conf.MONGODB_DOMAINS_COLLECTION)
    filter_query = {"domain": domain_name}
    update_data = {"$set": scan_data}
    collection.update_one(filter_query, update_data, upsert=True)


def mongodb_get_domain_scan(domain_name: str) -> dict | None:
    collection = get_mongo_collection(conf.MONGODB_DB_NAME, conf.MONGODB_DOMAINS_COLLECTION)
    result = collection.find_one({"domain": domain_name})
    return mongodb_result_to_json(result)

def mongodb_get_last_scans_by_type(scan_type: str, limit: int = 25) -> List[dict]:
    collection = get_mongo_collection(conf.MONGODB_DB_NAME, conf.MONGODB_DOMAINS_COLLECTION)
    cursor = (collection.find({"scan.type": scan_type, "scan.status": "completed"})
              .sort("scan.ended_at", DESCENDING)
              .limit(limit))
    results = list(cursor)
    # only return "scan" field
    results = list(map(lambda result: result["scan"], results))
    return mongodb_results_to_json(results)