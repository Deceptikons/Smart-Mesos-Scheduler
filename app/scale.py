import json
import scheduler
from scheduler import MyMesosScheduler
import logging
import mesos.interface
from mesos.interface import mesos_pb2
import mesos.native
from appConfig import AppConfig
from taskStatus import TaskStatus
import threading
class ScaleManager:
  def __init__(self,mesosSchedulerObj):
    print " Creating Obj"
    self.mesosObj=mesosSchedulerObj
  def scaleUp(self):
    app_obj = {'name':'test-app','cpu':'2','ram':'8196', 'command':'cd cassandra;./nonseed.sh;./startcassandra.sh;while sleep 5; do ps aux | grep java; done','docker_image':'yasaswikishore/cassandra:initialcommit','storage':'False'}
    app = AppConfig(app_obj)
    self.mesosObj.addApp(app)

  def scaleDown(self):
    print "Aithu"

