#!./flask/bin/python
from flask import Flask , request
import json
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
app = Flask(__name__)

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
           '10.10.1.71:5050') 
  # we start the scheduler driver in a daemon thread
  tdriver = threading.Thread( target = startScheduler , args= (driver,))
  tdriver.deamon = True
  tdriver.start()
  #finally, we run the application
  app.run()
