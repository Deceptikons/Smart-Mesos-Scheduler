#!/usr/bin/python
from flask import Flask , request , jsonify
import json
import requests
import scheduler
from scheduler import MyMesosScheduler
import logging
import scale
from scale import ScaleManager
import mesos.interface
from mesos.interface import mesos_pb2
import mesos.native
from appConfig import AppConfig
from taskStatus import TaskStatus
import threading
import subprocess
from subprocess import Popen, PIPE
app = Flask(__name__)


@app.before_request
def option_autoreply():
    """ Always reply 200 on OPTIONS request """

    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()

        headers = None
        if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
            headers = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']

        h = resp.headers

        # Allow the origin which made the XHR
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
        # Allow the actual method
        h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
        # Allow for 10 seconds
        h['Access-Control-Max-Age'] = "10"

        # We also keep current headers
        if headers is not None:
            h['Access-Control-Allow-Headers'] = headers

        return resp


@app.after_request
def set_allow_origin(resp):
    """ Set origin for GET, POST, PUT, DELETE requests """

    h = resp.headers

    # Allow crossdomain for other HTTP Verbs
    if request.method != 'OPTIONS' and 'Origin' in request.headers:
        h['Access-Control-Allow-Origin'] = request.headers['Origin']


    return resp



@app.route('/')
def api_root():
  return 'Welcome'

@app.route('/submit', methods=['POST'])
def submitJob():
  app_obj = request.get_json()
  print app_obj['name']
  #appdict = json.dumps(app_obj)
  #print appdict
  #print appdict['name']
  app = AppConfig(app_obj)
  mesosScheduler.addApp(app)
  return "Successfully submitted job" 


# Endpoint to get the task status
@app.route('/status', methods=['GET'])
def getStatus():
  #app_obj = request.get_json()
  #print app_obj['state']
  #if( app_obj['state'] == "up" ):
  #  print "Scaling up the Resources"
  #  scale_obj.scaleUp()
  #else:
  #  scale_obj.scaleDown()
  #appdict = json.dumps(app_obj)
  #print appdict
  #print appdict['name']
  #app = AppConfig(app_obj)
  print mesosScheduler.getTaskList()
  print jsonify(mesosScheduler.getTaskList())
  return json.dumps(mesosScheduler.getTaskList())

#Endpoint to get Application stdout log
@app.route('/appData')
def getData():
  appID = request.args.get('appID')
  p = Popen(['./go-mesoslog','-m', '127.0.0.1', 'print' , appID], stdin=PIPE, stdout=PIPE, stderr=PIPE)
  output, err = p.communicate(b"input data that is passed to subprocess' stdin")
  rc = p.returncode
  return output



#Endpoint to support DNS query
@app.route('/dnsQuery')
def getIPAddress():
  query = request.args.get('appID')
  request_string = "http://127.0.0.1:8123/v1/hosts/" + query + ".MyMesosDockerExample.mesos"
  response = requests.get(request_string)
  array = json.loads(response.text)
  ip_address = array[0]["ip"]

  print ip_address
  return ip_address


# Endpoint to get the state decisions (up or down)
@app.route('/status', methods=['POST'])
def submitStatus():
  app_obj = request.get_json()
  print app_obj['state']
  if( app_obj['state'] == "up" ):
    print "Scaling up the Resources"
    scale_obj.scaleUp()
  else:
    scale_obj.scaleDown()
  #appdict = json.dumps(app_obj)
  #print appdict
  #print appdict['name']
  #app = AppConfig(app_obj)
  #mesosScheduler.addApp(app)
  return "Successfully submitted status" 
''' a function to start the mesos scheduler
    this is an infinite loop, so needs to 
    be run on a separate thread as a daemon
'''

@app.route('/kill')
def killTask():
  taskID = request.args.get('taskID')
  print taskID
  driver.killTask(mesos_pb2.TaskID(value=taskID))
  return "Success"


def startScheduler(mesosdriver):
  mesosdriver.run()

#"Send MesosSCheduler obj"
def getObj():
  return mesosScheduler
if __name__ == '__main__':
  executor = mesos_pb2.ExecutorInfo()
  executor.executor_id.value = "mydocker"
  executor.name = "My docker example executor"
  
  framework = mesos_pb2.FrameworkInfo()
  framework.user = "" # Have Mesos fill in the current user.
  framework.name = "MyMesosDockerExample"

  implicitAcknowledgements = 1
  
  logging.basicConfig(level=logging.DEBUG)
  framework.principal = "docker-mesos-example-framework"
  mesosScheduler = MyMesosScheduler(implicitAcknowledgements, executor)

  # Creating obj of Scale Manager
  scale_obj = ScaleManager(mesosScheduler)


  # adding a custom application - this should be done by the REST API
  diction = {}
  diction["name"] = "test-app"
  diction["cpu"] = 2
  diction["ram"] = 512
  diction["command"] = "ifconfig; sleep 10"
  diction["docker_image"] = "centos"
  diction["storage"] = False
  print diction
  '''app = AppConfig(diction)
  mesosScheduler.addApp(app)'''
  print mesosScheduler.app_list
  driver = mesos.native.MesosSchedulerDriver(
       mesosScheduler,
           framework,
           '127.0.0.1:5050') 
  # we start the scheduler driver in a daemon thread
  tdriver = threading.Thread( target = startScheduler , args= (driver,))
  tdriver.deamon = True
  tdriver.start()
  #finally, we run the application
  app.run(host='127.0.0.1')
