import logging
import uuid
import time

from mesos.interface import Scheduler
from mesos.native import MesosSchedulerDriver
from mesos.interface import mesos_pb2

logging.basicConfig(level=logging.INFO)

def new_task(offer):
    task = mesos_pb2.TaskInfo()
    id = uuid.uuid4()
    task.task_id.value = str(id)
    task.slave_id.value = offer.slave_id.value
    task.name = "task {}".format(str(id))

    cpus = task.resources.add()
    cpus.name = "cpus"
    cpus.type = mesos_pb2.Value.SCALAR
    cpus.scalar.value = 1

    mem = task.resources.add()
    mem.name = "mem"
    mem.type = mesos_pb2.Value.SCALAR
    mem.scalar.value = 1

    return task


class HelloWorldScheduler(Scheduler):

    def registered(self, driver, framework_id, master_info):
        logging.info("Registered with framework id: {}".format(framework_id))

    def resourceOffers(self, driver, offers):
        logging.info("Recieved resource offers: {}".format([o.id.value for o in offers]))
        # whenever we get an offer, we accept it and use it to launch a task that
        # just echos hello world to stdout
        for offer in offers:
            task = new_task(offer)
            #task.command.value = "echo This Shit doesnt know how to end the program"
            task.command.value = "/home/venkat/a.out"
            time.sleep(2)
            logging.info("Launching task {task} "
                         "using offer {offer}.".format(task=task.task_id.value,
                                                       offer=offer.id.value))
            tasks = [task]
            driver.launchTasks(offer.id, tasks)

if __name__ == '__main__':
    # make us a framework
    framework = mesos_pb2.FrameworkInfo()
    framework.user = ""  # Have Mesos fill in the current user.
    framework.name = "hello-world1"
    driver = MesosSchedulerDriver(
        HelloWorldScheduler(),
        framework,
        "127.0.0.1:5050"  # assumes running on the master
    )
    driver.run()
