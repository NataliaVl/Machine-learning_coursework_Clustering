import pymongo
import hashlib
import os
import connection

def import_doc(path):
    f = open(path, 'r', encoding="utf-8")
    title = f.readline()

    doc = title + f.read()
    _line = doc.partition('Содержание статьи:\n')
    _l = _line[2].partition('\n\n')
    description = _l[0]

    hash_object = hashlib.md5(doc.encode())
    hash = hash_object.hexdigest()

    try:
        mydict = {"_id": hash, "doc": doc, "title": title, "description": description}
        x = col.insert_one(mydict)
        # export_md5_data(hash, doc)
    except Exception as e:
        print(e)

    f.close()


col = connection.connection_mongodb_texts()

directory = 'C://archive_storage_for_clustering'
files = os.listdir(directory)

for item in files:
    way = directory + "/" + item
    import_doc(way)
