#!/usr/bin/python
import logging
import mesos.interface
from mesos.interface import mesos_pb2
import mesos.native
from appConfig import AppConfig


class MyMesosScheduler(mesos.interface.Scheduler):

  def __init__(self, implicitAcknowledgements, executor):
    self.implicitAcknowledgements = implicitAcknowledgements
    self.executor = executor
    #configure logging
    self.logger = logging.getLogger('mesos_framework')
    formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    self.logger.addHandler(ch)
    self.app_list = []

  def registered(self, driver, frameworkId, masterInfo):
    self.logger.info("Registered with framework ID %s" % frameworkId.value)

  def addApp(self,appconfig):
    self.app_list.append(appconfig)

  def resourceOffers(self, driver, offers):
    '''
    Basic placement strategy (loop over offers and try to push as possible)
    '''
    id1 = 0
    for offer in offers:
      offer_tasks = []
      if (not self.app_list):
        break
      appconfig = self.app_list.pop()
      task = self.new_docker_task(offer, offer.id.value, appconfig)
      self.logger.info("testing logging after initializing task")
      offer_tasks.append(task)
      #id1 += 1
      driver.launchTasks(offer.id, offer_tasks)
      break
      self.logger.info("Finished ")	
      
    '''
    for offer in offers:
    self.logger.info(offer)
    # Let's decline the offer for the moment
    driver.declineOffer(offer.id)
    '''

  def statusUpdate(self, driver, update):
    '''
    when a task is over, killed or lost (slave crash, ....), this method
    will be triggered with a status message.
    '''
    self.logger.info("Task %s is in state %s" % \
    (update.task_id.value, mesos_pb2.TaskState.Name(update.state)))

  def frameworkMessage(self, driver, executorId, slaveId, message):
    self.logger.info("Received framework message")

  def new_docker_task(self, offer, id, appconfig):
    '''
    Creates a task for mesos

    :param offer: mesos offer
    :type offer: Offer
    :param id: Id of the task (unique)
    :type id: str
    :param appconfig: config of application to be launched
    :type appconfig: Appconfig
    '''
    task = mesos_pb2.TaskInfo()
    # We want of container of type Docker
    container = mesos_pb2.ContainerInfo()
    container.type = 1 # mesos_pb2.ContainerInfo.Type.DOCKER

    # Let's create a volume
    # container.volumes, in mesos.proto, is a repeated element
    # For repeated elements, we use the method "add()" that returns an object that can be updated
    if (appconfig.needStorage()):
      volume = container.volumes.add()
      volume.container_path = appconfig.getStorage() # Path in container
      #TODO: we need to generate paths on host based on hash
      volume.host_path = "/tmp/mesosexample" # Path on host
      volume.mode = 1 # mesos_pb2.Volume.Mode.RW
      #volume.mode = 2 # mesos_pb2.Volume.Mode.RO

    # Define the command line to execute in the Docker container
    command = mesos_pb2.CommandInfo()
    command.value = appconfig.getCmd()
    task.command.MergeFrom(command) # The MergeFrom allows to create an object then to use this object in an other one. Here we use the new CommandInfo object and specify to use this instance for the parameter task.command.

    task.task_id.value = id
    task.slave_id.value = offer.slave_id.value
    task.name = appconfig.getName() 

    # CPUs are repeated elements too
    cpus = task.resources.add()
    cpus.name = "cpus"
    cpus.type = mesos_pb2.Value.SCALAR
    cpus.scalar.value = appconfig.getCpus() 

    # Memory are repeated elements too
    mem = task.resources.add()
    mem.name = "mem"
    mem.type = mesos_pb2.Value.SCALAR
    mem.scalar.value = appconfig.getRam() 

    # Let's focus on the Docker object now
    docker = mesos_pb2.ContainerInfo.DockerInfo()
    docker.image = appconfig.getImage() 
    docker.network = 2 # mesos_pb2.ContainerInfo.DockerInfo.Network.BRIDGE
    docker.force_pull_image = True

    #create parameter object to pass the weave information
    param = docker.parameters.add()
    param.key = "net"
    param.value = "weave"

    # We could (optinally of course) use some ports too available in offer
    ## First we need to tell mesos we take some ports from the offer, like any other resource
    #mesos_ports = task.resources.add()
    #mesos_ports.name = "ports"
    #mesos_ports.type = mesos_pb2.Value.RANGES
    #port_range = mesos_ports.ranges.range.add()
    #available_port = get_some_available_port_in_port_offer_resources()
    #port_range.begin = available_port
    #port_range.end = available_port
    ## We also need to tell docker to do mapping with this port
    #docker_port = docker.port_mappings.add()
    #docker_port.host_port = available_port
    #docker_port.container_port = available_port

    # Set docker info in container.docker
    container.docker.MergeFrom(docker)
    # Set docker container in task.container
    task.container.MergeFrom(container)
    # Return the object
    return task

if __name__ == "__main__":
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
  # adding a custom application - this should be done by the REST API
  diction = {}
  diction["name"] = "test-app"
  diction["cpu"] = 2
  diction["ram"] = 512
  diction["command"] = "ifconfig; sleep 10"
  diction["docker_image"] = "centos"
  diction["storage"] = False
  app = AppConfig(diction)
  mesosScheduler.addApp(app)
  print mesosScheduler.app_list
  driver = mesos.native.MesosSchedulerDriver(
       mesosScheduler,
           framework,
           '10.10.1.71:5050') # I suppose here that mesos master url is local

  driver.run()

