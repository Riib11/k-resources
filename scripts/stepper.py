from subprocess import *
import datetime

# functions

# checks to see if the output is the kore-repl prompt
# returns None if not kore-repl prompt
# return nodeId if is prompt
def isMeaningful(output):
  return None # TODO

branches = [];

def saveTime(timeDuration, nodeIdStart, nodeIdStop):
  pass # TODO

# subprocess

output = ""
p = Popen(["cat"], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)

# nextNode

def pushNode():
  pass # TODO

# returns True if selected a node
# return False if no branches left
def popNode():
  # select the first node of a branch
  pass # TODO

def endOfBranch():
  pass # TODO

def isBranching():
  pass # TODO

def pushBranches():
  pass # TODO

# returns True if there is a next node is available, either by stepping or selecting a node and then being ready to step
# returns False if at end of branch and no branches left available to step
def nextNode():
  if endOfBranch():
    # if at the end of current branch, then select first node of next branch in stack; return True
    # if at the end of current branch, and no branches in the stack, then return False
    return popNode()
  
  # if stopped due to branching
  elif isBranching():
    # if there is branching, then push new branches to stack and select first node of one of them; return True
    pushBranches()
    return popNode()

# stepper script

while True:

  # timer start
  timeStart = time.time()

  # start stepping
  print("step 10\n", file=p.stdin)

  # wait for output (prompt + result)
  # loop:
  # - ignore if it is not what we want, continue
  # - if is what we want, then break loop
  while not isMeaningful():
    output = p.stdout.readline()

  # timer stop
  timeStop = time.time()

  # save time
  saveTime(timeStop - timeStart)

  if not nextNode(): break;

# TODO: save all branch step timing info to some file

# TODO: old

# write
print("hello world\n", file=p.stdin)
p.stdin.flush()

# read
print("output:", p.stdout.readline().rstrip("\n"))

# close
p.stdin.close()
p.stdout.close()
p.wait()

