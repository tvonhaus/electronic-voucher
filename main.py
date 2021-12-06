import flask
from flask import Flask, render_template, request, redirect, jsonify
import datetime
import pymongo
import os
import evoucherAPI as api
import createDB as create
from pymongo import MongoClient
from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse

app = Flask(__name__)

#Main page of webhook
@app.route('/')
def main():
	client = api.db_connect()
	#dbName = input("Input the name of the database you would like to connect to:")
	#api.createIssuer(db,"Taylor","+1519")
	#api.createBeneficiary(db,"Taylor","von Hausen","+1519")
	#api.createRedeemer(db,"Taylor","+1519")
	return render_template('index.html')

#Page where twilio SMS will be directed to
@app.route('/sms', methods = ['GET', 'POST'])

def sms_reply():
	print("Welcome to the sms webhook")
	client = api.db_connect()
	db = client['eVoucher2']
	body = request.values.get('Body',None)
	keywords = body.split()
	resp = MessagingResponse()
	
	if keywords[0] == "Issue":
		issuerNumber = request.form['From']
		if api.findIssuer(issuerNumber,db) is False:
			resp.message("Sorry you are not a recognized issuer. Please contact customer support for more info.")
		elif api.findBeneficiary(keywords[2],db) is False:
			resp.message("Sorry that beneficiary is not recognized. Please contact customer support for more info.")
		elif api.findItem(db,keywords[1]) is False:
			resp.message("Sorry that is not a recognized item. Please contact customer support for more info.")
		elif api.findVoucher1(db,keywords[2],keywords[1]) is True:
			resp.message("Sorry that beneficiary has already recieved a voucher of that type. Please contact customer support for more info.")
		else:
			resp.message("Issued " +keywords[1]+" to "+keywords[2])
			voucherID = api.createVoucher(db,keywords[2],keywords[1])
			api.sendVoucher(voucherID,keywords[2])
			api.issueLog(keywords[1],keywords[2],issuerNumber,db)
	elif keywords[0] == "Redeem":
		redeemerNumber = request.form['From']
		if api.findRedeemer(redeemerNumber,db) is False:
			resp.message("Sorry you are not a recognized redeemer. Please contact customer support for more info.")
		elif api.findItem(db,keywords[2]) is False:
			resp.message("Sorry that item is not registered. Please contact customer support for more info.")
		elif api.findVoucher2(db,keywords[1]) is False:
			resp.message("Sorry the voucher you are trying to redeem does not exist. Please contact customer support for more info.")
		else:
			api.redeemLog(keywords[2],db,resp)
			api.redeemVoucher(db,keywords[1],redeemerNumber)
			resp.message("Redeeming a voucher for the phone number: "+keywords[2])
	elif (keywords[0] == "Balance") or (keywords[0] == "Bal"):
		vouchers = db.Vouchers
		redeemerNumber = request.form['From']
		if api.findRedeemer(redeemerNumber,db) is True:
			redeemedCount = vouchers.count_documents({"Redeemer": redeemerNumber,"Status":"Redeemed"})
			resp.message("You have %d vouchers in the redeemed state." %(redeemedCount))
		else:
			resp.message("Sorry you are not a recognized retailer within the eVoucher system.")
	elif keywords[0] == "Ask":
		print("Thank you for your concern, we'll get back to you as soon as we can")
	else:
		print("Sorry your message format is not recognized")

	return str(resp)
@app.route('/home')
def home():
	client = api.db_connect()
	databases = client.list_database_names()
	return render_template('home.html',databases=databases)
@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/admin')
def adminPage():
	return render_template('admin.html')

@app.route('/createprogram',methods=['GET','POST'])
def createprogram():
	return render_template('createprogram.html')

@app.route('/programcreated',methods=['POST'])
def programcreated():
	dbname = request.form['dbname']

	create.createDB(dbname)
	if dbname:
		return jsonify({'dbname' : dbname})
	else:
		return jsonify({'Error': "Missing database name"})

@app.route('/program')
def program():
	dbname = request.args.get('db')
	api.use_db(dbname)

	return render_template('program.html',dbname = dbname)

@app.route('/program/logs')
def logs():
	dbname = request.args.get('db')
	db = api.use_db(dbname)
	logs = db.logs
	
	issueDocuments = logs.find({'Event':'Issue'},{'_id': 0})
	issueList = []
	for document in issueDocuments:
		issueList.append(document)

	redeemDocuments = logs.find({'Event':'Redeem'},{'_id': 0})
	redeemList = []
	for document in redeemDocuments:
		redeemList.append(document)

	voucherDocuments = logs.find({'Event':'Voucher created'},{'_id': 0})
	voucherList = []
	for document in voucherDocuments:
		voucherList.append(document)

	logDocuments = logs.find({},{'_id': 0})
	logList = []
	for document in logDocuments:
		print(document)
		logList.append(document)
	print(logList)
	return render_template('logs.html',logList = logList,issueList = issueList,redeemList = redeemList, voucherList = voucherList)

if __name__ == '__main__':
	app.run(debug=True)
