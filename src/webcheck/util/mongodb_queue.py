from collections import abc
from datetime import datetime, timezone

import pymongo
from pymongo import ReturnDocument

from webcheck import conf


class JobQueue:

    @abc.abstractmethod
    def enqueue(self, item):
        pass

    @abc.abstractmethod
    def dequeue(self):
        pass

    @abc.abstractmethod
    def is_empty(self) -> bool:
        pass

    @abc.abstractmethod
    def count(self) -> int:
        pass


class SimpleInMemoryQueue(JobQueue):

    def __init__(self):
        self.queue = []

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if self.queue:
            return self.queue.pop(0)
        return None

    def count(self):
        return len(self.queue)

    def is_empty(self) -> bool:
        return len(self.queue) == 0


class MongoDBQueue(JobQueue):

    def __init__(self, mongo_uri: str, db_name: str, collection_name: str):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.worker_id = "worker_" + str(datetime.now().timestamp())

        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def enqueue(self, item):
        doc = {
            "payload": item,
            "status": "queued",
            "enqueued_at": datetime.now(timezone.utc),
            "locked_at": None,
            "locked_by": None,
        }
        result = self.collection.insert_one(doc)
        return str(result.inserted_id)

    def dequeue(self):
        """Get the oldest queued job and lock it for this worker."""
        now = datetime.now(timezone.utc)

        job = self.collection.find_one_and_update(
            filter={
                "status": "queued",
            },
            update={
                "$set": {
                    "status": "processing",
                    "locked_at": now,
                    "locked_by": self.worker_id,
                }
            },
            sort=[("enqueued_at", pymongo.ASCENDING)],  # FIFO!
            return_document=ReturnDocument.AFTER
        )

        #return job.get("payload") if job else None
        return job

    def is_empty(self) -> bool:
        count = self.collection.count_documents({"status": "queued"})
        return count == 0

    def count(self) -> int:
        return self.collection.count_documents({"status": "queued"})

    def mark_done(self, job_id):
        self.collection.update_one(
            {"_id": job_id},
            {"$set": {"status": "done", "locked_at": None, "locked_by": None}}
        )

    def mark_failed(self, job_id, reason: str):
        self.collection.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": "failed",
                    "failure_reason": reason,
                    "locked_at": None,
                    "locked_by": None
                }
            }
        )

def simple_queue_handler():
    """
    Initialize a simple in-memory queue.
    """
    return SimpleInMemoryQueue()

def mongodb_queue_handler():
    """
    Initialize MongoDB queue and attach it to the FastAPI app.
    """
    mongo_queue = MongoDBQueue(
        mongo_uri=conf.MONGODB_URI,
        db_name=conf.MONGODB_DB_NAME,
        collection_name=conf.MONGODB_QUEUE_COLLECTION,
    )
    return mongo_queue
