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
client = MongoClient("mongodb+srv://izaan:microsoft123@csapl.hsqoz.mongodb.net/test?authSource=admin&replicaSet=atlas-run4dp-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true", ssl_cert_reqs=ssl.CERT_NONE)

@app.route('/data_handling', methods=['POST'])
def process_image():
    db = client['Reception_Name']
    VisitorsData = db.Visitors

    if request.method == "POST":
        data = request.json
        data['name'] = data['name'].lower()
        data['organization_name'] = data['organization_name'].lower()
        data['Contact_Person'] = data['Contact_Person'].lower()
        data['Visit_Purpose'] = data['Visit_Purpose'].lower()
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
                if entry["cnic"] == cnic:
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
        non_check = 0
        for k, v in filter.items():  
            if k == "From":
                fromdate = v
                val = 1
            elif k == "To":
                todate = v
                val1 = 1
            elif k == "Non_Checked_Out":
                non_check = 1
            elif k == "name" or k == "organization_name":
                dict1[k] = v.lower()
            else:
                dict1[k] = v

        if val == 0 and val1 == 0 :
            visitor = VisitorsData.find(dict1)
            if visitor != None:
                if non_check == 1:
                    query = []
                    for entry in visitor:
                        if entry["Check_Out_Date"] == "":
                            query.append(entry)
                    if query != None:
                        visitor = list(map(something, query))
                        return {'result': visitor}
                    else:
                        return {"result": "Data Fetch Failed"}
                else:
                    visitor = list(map(something, visitor))
                    return {'result': visitor}
            else:
                return {"result": "Data Fetch Failed"}

        elif val == 1 and val1 == 0:
            visitor = VisitorsData.find({"Check_In_Date": {'$regex': '^'+fromdate} ,**dict1})
            if visitor != None:
                if non_check == 1:
                    query = []
                    for entry in visitor:
                        if entry["Check_Out_Date"] == "":
                            query.append(entry)
                    if query != None:
                        visitor = list(map(something, query))
                        return {'result': visitor}
                    else:
                        return {"result": "Data Fetch Failed"}
                else:
                    visitor = list(map(something, visitor))
                    return {'result': visitor}
            else:
                return {"result": "Data Fetch Failed"}

        elif val == 0 and val1 == 1:
            visitor = VisitorsData.find({"Check_In_Date": {'$regex': '^'+todate}, **dict1})
            if visitor != None:
                if non_check == 1:
                    query = []
                    for entry in visitor:
                        if entry["Check_Out_Date"] == "":
                            query.append(entry)
                    if query != None:
                        visitor = list(map(something, query))
                        return {'result': visitor}
                    else:
                        return {"result": "Data Fetch Failed"}
                else:
                    visitor = list(map(something, visitor))
                    return {'result': visitor}
            else:
                return {"result": "Data Fetch Failed"}

        elif val == 1 and val1 == 1:            
            visitor = VisitorsData.find(dict1)
            if visitor != None:
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
                    if date >= fromdate and date <= todate:
                        query.append(entry)
                if query != None:
                    if non_check == 1:
                        query1 = []
                        for entry in query:
                            if entry["Check_Out_Date"] == "":
                                query1.append(entry)
                        if query1 != None:
                            visitor = list(map(something, query1))
                            return {'result': visitor}
                        else:
                            return {"result": "Data Fetch Failed"}
                    else:
                        visitor = list(map(something, query))
                        return {'result': visitor}
            else:
                return {"result": "Data Fetch Failed"}

@app.route('/login', methods=["POST"])
def login():
    if request.method == "POST":
        data = request.json
        if(data['username'] == "reception" and data['password'] == "csapl.123"):
            return {"token": "1234"}
        elif(data['username'] == "admin" and data['password'] == "isadmin"):
            return {"token": "1234"}
         
@app.route('/regular', methods=["POST","GET"])
def regular():
    db = client['Reception_Name']
    VisitorsData = db.Regulars
    if request.method == "POST":
        info = {'profession':'', 'name': '', 'cnic': '' , 'timing' : []}
        data = request.json
        profession = data['profession'].lower()
        name = data['name'].lower()
        cnic = data['cnic']
        time = data['date']
        additional_info = data['additional_info'].lower()
        visitor = VisitorsData.find_one({"cnic": cnic})
        if visitor != None:
            visitor['profession'] = profession
            visitor['name'] = name
            visitor['cnic'] = cnic
            visitor['additional_info'] = additional_info
            visitor['timing'].append(time)
            VisitorsData.update_one({"cnic": cnic},{"$set": visitor})
        else:
            info["profession"] = profession
            info["name"] = name
            info['cnic'] = cnic
            info["additional_info"] = additional_info
            info['timing'].append(time)
            VisitorsData.insert_one(info)

        return {'result': "Data entry noted"}

    if request.method == "GET":

        def something(visitor):
                visitor["_id"] = str(visitor["_id"])
                return visitor

        filter = request.args
        dict1 = {}
        val =  0
        val1 = 0
        for k, v in filter.items():  
            if k == "From":
                fromdate = v
                val = 1
            elif k == "To":
                todate = v
                val1 = 1
            elif k == "name" or k == "profession" or k == "additional_info":
                dict1[k] = v.lower()
            else:
                dict1[k] = v

        if val == 0 and val1 == 0:
            visitor = VisitorsData.find(dict1)
            if visitor != None:
                visitor = list(map(something, visitor))
                return {'result': visitor}
            else:
                return {"result": "Data Fetch Failed"}

        elif val == 1 and val1 == 0:
            visitor = VisitorsData.find(dict1)
            query = []
            query1 = []
            for entry in visitor:
                for num in entry['timing']:
                    num = num.split('T')
                    if num[0] == fromdate:
                        query.append(entry['profession'])
                        query.append(entry['name'])
                        query.append(entry['cnic'])
                        query.append(num[0])
                        query1.append(query)
                        query = []
            if query1 != None:
                return {'result': query1}
            else:
                return {"result": "Data Fetch Failed"}
                
        elif val == 0 and val1 == 1:
            visitor = VisitorsData.find(dict1)
            query = []
            query1 = []
            for entry in visitor:
                for num in entry['timing']:
                    num = num.split('T')
                    if num[0] == todate:
                        query.append(entry['profession'])
                        query.append(entry['name'])
                        query.append(entry['cnic'])
                        query.append(num[0])
                        query1.append(query)
                        query = []
            if query1 != None:
                return {'result': query1}
            else:
                return {"result": "Data Fetch Failed"}

        elif val == 1 and val1 == 1:
            visitor = VisitorsData.find(dict1)
            if visitor != None:
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

                print("this is from date: ",fromdate)
                print("this is to date: ",todate)
                query = []
                query1 = []
                for entry in visitor:
                    for date in entry['timing']:
                        date = date.split('T')
                        date = date[0]
                        date = date.split('-')
                        day = date[2]
                        month = date[1]
                        year = date[0]
                        date = datetime.datetime(int(year), int(month), int(day))
                        print(date)
                        if date >= fromdate and date <= todate:
                            query.append(entry['profession'])
                            query.append(entry['name'])
                            query.append(entry['cnic'])
                            query.append(date)
                            query1.append(query)
                            query = []
                if query1 != None:
                    return {'result': query1}
                else:
                    return {"result": "Data Fetch Failed"}
            else:
                return {"result": "Data Fetch Failed"}
               

app.run(host="localhost")
# waitress.serve(app, port=5000)
