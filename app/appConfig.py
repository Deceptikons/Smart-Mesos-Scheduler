#!/usr/bin/python
''' This class stores the configuration of the app
	string name
	int    numcpu
	int	   ram
  string docker_image
	bool   storage
	string container-path
	string host-path (generated by the scheduler?)
  string command
'''
''' TODO: add prometheus queries also to the appConfig
          add support for number of instances
'''
class AppConfig:
  ''' constructor takes a dictionary (prolly from a JSON)
      as a parameter
  '''
  def __init__(self, diction):
    print diction
    self.name = diction['name']
    self.cpus = int(diction["cpu"])
    self.ram  = int(diction["ram"])
    self.command = diction["command"]
    self.storage = (diction["storage"]!="False")
    self.dockerImage = diction["docker_image"]
    if (self.storage):
      self.container_path = diction["container_path"]

  #accessor functions for each
  def getName(self):
    return self.name

  def getCpus(self):
    return self.cpus

  def getRam(self):
    return self.ram

  def getCmd(self):
    return self.command

  def getImage(self):
    return self.dockerImage

  def needStorage(self):
    return self.storage

  def getStorage(self):
    if (self.storage==False):
      return None
    else:
      return self.container_path

  def getCommand(self):
    return command
