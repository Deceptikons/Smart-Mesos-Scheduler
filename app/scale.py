import json
import scheduler
from scheduler import MyMesosScheduler
import logging
import time
import mesos.interface
from mesos.interface import mesos_pb2
import mesos.native
from appConfig import AppConfig
from taskStatus import TaskStatus
import threading
class ScaleManager:
  id = 0
  def __init__(self,mesosSchedulerObj):
    print " Creating Obj"
    self.mesosObj=mesosSchedulerObj
  def scaleUp(self):
    ScaleManager.id+=1
    app_obj = {'name':'test-app'+str(ScaleManager.id),'cpu':'1','ram':'8196', 'command':'cd cassandra;./nonseed.sh;./startcassandra.sh;while sleep 5; do ps aux | grep java; done','docker_image':'yasaswikishore/cassandra:initialcommit','storage':'False'}
    app = AppConfig(app_obj)
    self.mesosObj.addApp(app)
    print "Submitted Non Seed Node"
    time.sleep(60)
    prometheus_obj ={'name':'prometheus','cpu':'0.5','ram':'1024', 'command':'cd prometheus;./config.sh '+str(app_obj['name'])+' 10.10.1.71;./prometheus;while sleep 5; do ps aux | grep prometheus; done','docker_image':'yasaswikishore/prometheus','storage':'False'}
    app = AppConfig(prometheus_obj)
    self.mesosObj.addApp(app)
    print "Submitted prometheus Node"

  def scaleDown(self):
    print "Aithu"

