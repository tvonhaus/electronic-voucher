import flask
from flask import Flask, render_template, request, redirect
import pymongo
import os
import string
import random
import datetime
from twilio.rest import Client
from pymongo import MongoClient

"""
Attempts to connect to the MongoDB server
Returns client to be used to specify a database
"""
def db_connect():
    try:
        client = MongoClient('mongodb://localhost:27017')
    except:
        print("Connection failed")

    return client

"""
Connects to a database of the specified name
Returns the db.
"""
def use_db(dbName):
    client = db_connect()
    db = client[dbName]
    print("Connected to: " + dbName)
    return db

"""
Attempts to find a matching phone number within the logs collection.
If no match is found a boolean False is returned.
If a match is found a boolean True is returned.
"""
def findBeneficiary(toFind,db):
    benefics = db.Beneficiaries
    match = benefics.find_one({"Business Phone": toFind})
    if match is None:
        return False
    else:
        return True


"""
Connects to the Issuers collection and attempts to find a
certain phone number within the collection.
If no match is found, returns False. If a match is found returns True.
"""
def findIssuer(toFind,db):
    issuers = db.Issuers
    match = issuers.find_one({"Phone Number": toFind })
    if match is None:
        return False
    else:
        return True


"""
Connects to the logs collection and creates a log document with the event, item type,
date, and beneficiary
"""
def issueLog(item,benPhone,issuePhone,db):
    logs = db.logs
    benefics = db.Beneficiaries
    issuers = db.Issuers
    beneficiary = benefics.find_one({"Phone Number": benPhone})
    issuer = issuers.find_one({"Phone Number": issuePhone})

    log = {
        "Event": "Issue",
        "Item Issued": item,
        "Date": datetime.datetime.utcnow(),
        "Issuer Phone": issuePhone,
        "Beneficiary Phone": benPhone
    }

    log_id = logs.insert_one(log).inserted_id
    log_id


"""

"""
def redeemLog(phoneNumber,db,response):
    logs = db.logs
    log = {
        "Event": "Redeem",
        "Date": datetime.datetime.utcnow(),
        "Redemption Status" : "Success"
        }
    log_id = logs.insert_one(log).inserted_id
    log_id

"""
Generates a voucher ID and creates and adds a voucher to the voucher collection.
"""
def createVoucher(db,beneficiaryNum,item):
    chars = string.ascii_lowercase + string.digits
    voucherID = ''.join(random.choice(chars) for _ in range(8))
    vouchers = db.Vouchers
    logs = db.logs

    voucher = {
        "Voucher Code": voucherID,
        "Status": "Issued",
        "Beneficiary Number": beneficiaryNum,
        "Item Type": item
    }
    try:
        voucher_id = vouchers.insert_one(voucher).inserted_id
        voucher_id
        log = {
            "Event": "Voucher created",
            "Date": datetime.datetime.utcnow(),
            "Voucher": voucher,
            "Result": "Success"
        }
    except:
        log = {
            "Event": "Voucher created",
            "Date": datetime.datetime.utcnow(),
            "Voucher": voucher,
            "Result": "Fail"
        }

    log_id = logs.insert_one(log).inserted_id
    log_id

    return voucherID

"""
Checks the Vouchers collection for a voucher with a matching
beneficiary number and item type. If it exists returns true,
if it does not exist returns false.
"""
def findVoucher1(db,beneficiaryNum,item):
    vouchers = db.Vouchers
    match = vouchers.find_one({"Beneficiary Number": beneficiaryNum,"Item Type": item})
    if match is None:
        return False
    else:
        return True


def findVoucher2(db,voucherCode):
    vouchers = db.Vouchers
    match = vouchers.find_one({"Voucher Code": voucherCode})
    if match is None:
        return False
    else:
        return True
"""
Checks the Items collection for an item with a matching item type. If
a match is found it returns true. If no match is found, returns false.
"""
def findItem(db,itemType):
    items = db.Items
    match = items.find_one({"Item Type": itemType})
    if match is None:
        return False
    else:
        return True

"""
Searches the redeemers collection for a redeemer with a matching phone number.
If a match is found, returns True. If no match is found, returns False.
"""
def findRedeemer(toFind,db):
    redeemers = db.Redeemers
    match = redeemers.find_one({"Phone Number": toFind})
    if match is None:
        return False
    else:
        return True

"""
Finds a voucher in the voucher collection based on its voucher code and updates its
status to redeemed as well as updates the redeemer number.
"""
def redeemVoucher(db,voucherCode,redeemNumber):
    vouchers = db.Vouchers
    toRedeem = vouchers.update_one({"Voucher Code": voucherCode},{ "$set": {"Status": "Redeemed", "Redeemer": redeemNumber}})

"""
Sends a voucher code to a specified beneficiary number.
"""
def sendVoucher(voucherCode,beneficiaryNum):
    account_sid = 'AC94ea8c24e9df3fe2c05bd281f59c1128'
    auth_token = '0933ef39ab0c1cd878ca0b148fea619d'
    client = Client(account_sid,auth_token)
    messageText = 'Voucher: ' + voucherCode
    print(messageText)
    message = client.messages.create(
    from_ ='+12264007393',
    body=messageText,
    to= beneficiaryNum
    )


"""
Creates and inserts an issuer into the Issuers collection of a database.
"""
def createIssuer(db,title,issuerNum):
    issuers = db.Issuers
    issuer = {
        "Title": title,
        "Phone Number": issuerNum
    }
    issuer_id = issuers.insert_one(issuer).inserted_id
    issuer_id

    logs = db.Logs
    log = {
        "Event": "Issuer created",
        "Date": datetime.datetime.utcnow(),
        "Issuer Title": title,
        "Issuer Phone Number": issuerNum
    }
    log_id = logs.insert_one(log).inserted_id
    log_id

"""
Creates and inserts a beneficiary into the Beneficiaries collection of a
database.
"""
def createBeneficiary(db,fname,lname,beneficaryNum):
    beneficiaries = db.Beneficiaries
    beneficiary = {
        "First Name": fname,
        "Last Name": lname,
        "Business Phone": beneficaryNum,
    }
    beneficiary_id = beneficiaries.insert_one(beneficiary).inserted_id
    beneficiary_id

    logs = db.Logs
    log = {
        "Event": "Beneficiary created",
        "Date": datetime.datetime.utcnow(),
        "Beneficiary Phone Number": beneficaryNum
    }
    log_id = logs.insert_one(log).inserted_id
    log_id

"""
Creates and inserts a redeemer into the Redeemers collection of a database.
"""
def createRedeemer(db,title,redeemerNum):
    redeemers = db.Redeemers
    redeemer = {
        "Title": title,
        "Phone Number": redeemerNum
    }

    logs = db.Logs
    log = {
        "Event": "Redeemer created",
        "Date": datetime.datetime.utcnow(),
        "Redeemer Title": title,
        "Redeemer Phone Number": redeemerNum
    }
    log_id = logs.insert_one(log).inserted_id
    log_id
