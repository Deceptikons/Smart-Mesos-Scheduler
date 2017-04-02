''' we define a class that stores task status for each
    application that is launched
    this should be query-able as well as write-able
    Usage:
        obj = TaskStatus()
        obj.addApp("name_of_application")
        obj.addTask("task_id", "name_of_application")
'''

class TaskStatus:
  def __init__(self):
    self.list_of_dicts = {}
    self.task_reverse_lookup = {}

  def addApp(self, app_name):
    if (app_name in self.list_of_dicts):
      return
    self.list_of_dicts[app_name] = {}

  def addTask(self, task_id, app_name):
    #sanity check for app_name
    print app_name
    print self.list_of_dicts[app_name]
    self.list_of_dicts[app_name][task_id] = "Unknown"
    self.task_reverse_lookup[task_id] = app_name

  def updateStatus(self, task_id, status):
    #get the name of the app
    app_name = self.task_reverse_lookup[task_id]
    #update the status
    self.list_of_dicts[app_name][task_id] = status

  #get the dictionary for logging purposes
  def getDict(self):
    return self.list_of_dicts



