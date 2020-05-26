import os
import pymongo


mongodb = pymongo.MongoClient("mongodb://localhost:27017/")

# запуск серверов
def start_mongodb_server():
    os.system(r'C:\Users\Natasha\mongodb\bin\mongod.exe')


def connection_mongodb_texts():
    db = mongodb["machine_learning"]
    col = db["texts"]
    return col

