from subprocess import Popen, PIPE
appID = "cassandraseed"
p = Popen(['./go-mesoslog','-m', '10.10.1.71', 'print' , appID], stdin=PIPE, stdout=PIPE, stderr=PIPE)
output, err = p.communicate(b"input data that is passed to subprocess' stdin")
rc = p.returncode
print output
