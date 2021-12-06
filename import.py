import csv
import sys
import collections
import datetime
import evoucherAPI as api

with open(sys.argv[1],newline='') as csvfile:
    reader = csv.DictReader(csvfile,fieldnames =("(Do Not Modify) Contact","(Do Not Modify) Row Checksum","(Do Not Modify) Modified On","First Name","Last Name","Business Phone"))
    client = api.db_connect()
    dbName = input("Please input the database you would like to import to:")
    db = client[dbName]
    benefics = db.Beneficiaries
    duplicateCount = 0
    beneficiaryCount = 0
    next(csvfile)
    for row in reader:
        print(row)
        items = list(row.values())
        match = benefics.find_one({"Business Phone": items[2]})
        if match is None:
            benefics.insert_one(row)
            print("Inserted.")
            beneficiaryCount += 1

            logs = db.logs
            log = {
                "Event": "Import Beneficiary",
                "Result": "Success",
                "Beneficiary First Name": items[0],
                "Beneficiary Last Name": items[1],
                "Beneficiary Number": items[2],
                "Date": datetime.datetime.utcnow(),
            }
            log_id = logs.insert_one(log).inserted_id
            log_id
        else:
            duplicateCount += 1
            print("Sorry, contact "+items[0],items[1]+" is already on the list of beneficiaries. If this is an issue please contact customer support")
            logs = db.logs
            log = {
                "Event": "Import Beneficiary",
                "Result": "Fail",
                "Beneficiary First Name": items[0],
                "Beneficiary Last Name": items[1],
                "Beneficiary Number": items[2],
                "Date": datetime.datetime.utcnow(),
            }
            log_id = logs.insert_one(log).inserted_id
            log_id


print(beneficiaryCount, " new beneficiaries were imported.")
print(duplicateCount, " duplicates were not imported.")
