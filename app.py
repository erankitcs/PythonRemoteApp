from flask import Flask,render_template,jsonify,json,request
from pymongo import MongoClient
from bson.objectid import ObjectId
from fabric import Connection

application = Flask(__name__)

client=MongoClient('mongodb://localhost')

db=client.MachineData

@application.route('/')
def showMachineList():
    return render_template('list.html')

@application.route('/addMachine',methods=['POST'])
def addMachine():
    try:
        json_data=request.json['info']
        deviceName = json_data['device']
        ipAddress = json_data['ip']
        userName = json_data['username']
        password = json_data['password']
        portNumber = json_data['port']
        machine={'device':deviceName,'ip':ipAddress,'username':userName,'password':password,'port':portNumber}
        db.Machines.insert_one(machine)
        return jsonify(status='OK',message='inserted successfully')
    except Exception as e:
        return jsonify(status='ERROR',message=str(e))

@application.route('/getMachine',methods=['POST'])
def getMachine():
    try:
        machineId = request.json['id']
        print(machineId)
        machine = db.Machines.find_one({'_id':ObjectId(machineId)})
        print(machine)
        machineDetail = {
                'device':machine['device'],
                'ip':machine['ip'],
                'username':machine['username'],
                'password':machine['password'],
                'port':machine['port'],
                'id':str(machine['_id'])
                }
        return json.dumps(machineDetail)
    except Exception as e:
        return str(e)

@application.route('/updateMachine',methods=['POST'])
def updateMachine():
    try:
        machineInfo = request.json['info']
        machineId = machineInfo['id']
        device = machineInfo['device']
        ip = machineInfo['ip']
        username = machineInfo['username']
        password = machineInfo['password']
        port = machineInfo['port']

        db.Machines.update_one({'_id':ObjectId(machineId)},{'$set':{'device':device,'ip':ip,'username':username,'password':password,'port':port}})
        return jsonify(status='OK',message='updated successfully')
    except Exception as e:
        return jsonify(status='ERROR',message=str(e))


@application.route("/deleteMachine",methods=['POST'])
def deleteMachine():
    try:
        machineId = request.json['id']
        db.Machines.remove({'_id':ObjectId(machineId)})
        return jsonify(status='OK',message='deletion successful')
    except Exception as e:
        return jsonify(status='ERROR',message=str(e))

@application.route('/getMachineList',methods=['POST'])
def getMachineList():
    try:
        cursor=db.Machines.find({})
        machineList=[]
        for machine in cursor:
            print(machine)
            machineItem={
            'device':machine['device'],
            'ip':machine['ip'],
            'username':machine['username'],
            'password':machine['password'],
            'port':machine['port'],
            'id':str(machine['_id'])
            }
            machineList.append(machineItem)
    except Exception as e :
         return str(e)
    return json.dumps(machineList)

@application.route("/execute",methods=['POST'])
def execute():
    try:
        machineInfo=request.json['info']
        ip = machineInfo['ip']
        username = machineInfo['username']
        password = machineInfo['password']
        command = machineInfo['command']
        isRoot = machineInfo['isRoot']

        #env.host_string=username+'@'+ip
        #env.password=password
        resp=''
        #print(host_string)
        with Connection(ip,user=username,connect_kwargs={'password':password}) as c :
            if isRoot:
                resp=c.sudo(command)
            else:
                resp=c.run(command)
        #print(to_string(resp))
        return jsonify(status='OK',message=resp.stdout.strip())
    except Exception as e:
        print ('Error is ' , str(e))
        return jsonify(status='ERROR',message=str(e))
if __name__=='__main__':
    application.run(host='localhost',debug='true')
