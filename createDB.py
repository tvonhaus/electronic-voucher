import flask
import pymongo
import datetime
import sys
import evoucherAPI as api


def createDB(newDB):
    client = api.db_connect()

    #dbName = input("Input a name for the database:")
    dbName = newDB
    databases = client.list_database_names()
    if dbName in databases:
        print("Database of that name already exists")
    elif (dbName is "") or (dbName is " "):
        print("Database name is empty")
    else:
        db = client[dbName]

        beneficiaries = db["Beneficiaries"]
        info = {
            "Event": "Collection Created",
            "Collection Name": "Beneficiaries",
            "Date": datetime.datetime.utcnow()
            }
        info_id = beneficiaries.insert_one(info).inserted_id
        info_id

        issuers = db["Issuers"]
        info = {
            "Event": "Collection Created",
            "Collection Name": "Issuers",
            "Date": datetime.datetime.utcnow()
            }
        info_id = issuers.insert_one(info).inserted_id
        info_id

        items = db["Items"]
        info = {
            "Event": "Collection Created",
            "Collection Name": "Items",
            "Date": datetime.datetime.utcnow()
            }
        info_id = items.insert_one(info).inserted_id
        info_id

        redeemers = db["Redeemers"]
        info = {
            "Event": "Collection Created",
            "Collection Name": "Redeemers",
            "Date": datetime.datetime.utcnow()
            }
        info_id = redeemers.insert_one(info).inserted_id
        info_id

        vouchers = db["Vouchers"]
        info = {
            "Event": "Collection Created",
            "Collection Name": "Vouchers",
            "Date": datetime.datetime.utcnow()
            }
        info_id = vouchers.insert_one(info).inserted_id
        info_id

        logs = db["Logs"]
        info = {
            "Event": "Collection Created",
            "Collection Name": "Logs",
            "Date": datetime.datetime.utcnow()
            }
        info_id = logs.insert_one(info).inserted_id
        info_id
