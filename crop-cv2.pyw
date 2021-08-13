from re import split
import datetime
import ssl
from flask import Flask, request
from pymongo import MongoClient
from flask_cors import CORS
import waitress
app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = False
client = MongoClient("mongodb+srv://superman:isadmin@csapl.3t7kz.mongodb.net/test", ssl_cert_reqs=ssl.CERT_NONE)

@app.route('/data_handling', methods=['POST', "GET"])
def process_image():
    db = client['Reception_Name']
    VisitorsData = db.Visitors

    if request.method == "POST":
        data = request.json
        insert = VisitorsData.insert_one(data)
        if insert != None:
            return {"result": "Data Sucessfully Inserted into Database"}
        else:
            return {"result": "Insertion failed"}

@app.route('/home_screen_renderer', methods=["GET"])
def home_screen():
    db = client['Reception_Name']
    VisitorsData = db.Visitors

    if request.method == "GET":
        date = request.args.get('date')
        defaulter = 0
        defaulter = VisitorsData.count_documents({"Check_Out_Date": ""})
        visitor = VisitorsData.find({"Check_In_Date": {'$regex': '^'+date}})
        if visitor != None:
            total = 0
            checkout = 0
            for entry in visitor:
                total += 1
                if entry["Check_Out_Date"] != '':
                    checkout = checkout + 1

            remaining = total - checkout
            defaulter = defaulter - remaining
            return {
                'total': total,
                'checkout': checkout,
                'remaining': remaining,
                'defaulter': defaulter
            }
        else:
            return {'result': "Data Fetch Failed"}

@app.route('/checkout_screen', methods=["GET", "POST"])
def checkout_screen():
    db = client['Reception_Name']
    VisitorsData = db.Visitors

    if request.method == "GET":
        date = request.args.get('date')
        visitor = VisitorsData.find({"Check_Out_Date": "", "Check_In_Date": {'$regex': '^'+date}})
        if visitor != None:
            def something(visitor):
                visitor["_id"] = str(visitor["_id"])
                return visitor

            visitor = list(map(something, visitor))
            return {'result': visitor}
        else:
            return {'result': "Data Fetch Failed"}

    if request.method == "POST":
        data = request.json
        date = data['body']['Check_In_Date']
        checkout = data['body']['Check_Out_Date']
        cnic = data['body']['cnic']
        date = date.split('T')
        date = date[0]
        visitor = {}
        visitor1 = VisitorsData.find({"Check_Out_Date": "", "Check_In_Date": {'$regex': '^'+date}})
        if visitor1 != None:
            count = VisitorsData.count_documents(
                {"Check_Out_Date": "", "Check_In_Date": {'$regex': '^'+date},"cnic" : cnic})
            val = 0
            for entry in visitor1:
                val += 1
                if entry["cnic"] == cnic and val == count:
                    entry["Check_Out_Date"] = checkout
                    visitor = VisitorsData.update_one({'_id': entry['_id']}, {'$set': entry})
            if visitor != None:        
                return {'Success': "Your checkout time has been noted."}
            else:
                return {"result": "Data Update Failed"}
        else:
            return {"result": "Data Fetch Failed"}

@app.route('/search_screen', methods=["GET"])
def search_screen():
    db = client['Reception_Name']
    VisitorsData = db.Visitors

    if request.method == "GET":
        def something(visitor):
            visitor["_id"] = str(visitor["_id"])
            return visitor

        filter = request.args
        dict1 = {}
        val =  0
        val1 = 0
        for k, v in filter.items():  
            if k == "Check_In_Date":
                todate = v
                val = 1
            elif k == "Check_Out_Date":
                fromdate = v
                val1 = 1
            else:
                dict1[k] = v

        if val == 0 and val1 == 0 :
            visitor = VisitorsData.find(dict1)
            
        elif val == 1 and val1 == 0:
            visitor = VisitorsData.find({"Check_In_Date": {'$regex': '^'+todate} ,**dict1})

        elif val == 0 and val1 == 1:
            visitor = VisitorsData.find({"Check_In_Date": {'$regex': '^'+fromdate}, **dict1})
            
        elif val == 1 and val1 == 1:            
            visitor = VisitorsData.find(dict1)
            todate = todate.split("-")
            day = todate[2]
            month = todate[1]
            year = todate[0]
            todate = datetime.datetime(int(year), int(month), int(day))

            fromdate = fromdate.split("-")
            day = int(fromdate[2])
            month = fromdate[1]
            year = fromdate[0]
            fromdate = datetime.datetime(int(year), int(month), int(day))

            query = []
            for entry in visitor:
                date = entry['Check_In_Date']
                date = date.split('T')
                date = date[0]
                date = date.split('-')
                day = date[2]
                month = date[1]
                year = date[0]
                date = datetime.datetime(int(year), int(month), int(day))
                if date >= todate and date <= fromdate:
                    query.append(entry)
            if query != None:
                visitor = list(map(something, query))
                return {'result': query}
            else:
                return {"result": "Data Fetch Failed"}

        if visitor != None:
            visitor = list(map(something, visitor))
            return {'result': visitor}
        else:
            return {"result":"Data Fetch Failed"}

@app.route('/login', methods=["POST"])
def login():
    if request.method == "POST":
        data = request.json
        if(data['username'] == "reception" and data['password'] == "csapl.123"):
            return {"token": "1234"}
        elif(data['username'] == "admin" and data['password'] == "isadmin"):
            return {"token": "1234"}
        
#app.run(host="localhost")
waitress.serve(app, port=5000)
