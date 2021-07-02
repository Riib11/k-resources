from subprocess import *
import time

# p = Popen(["grep", "a"], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True, ) # bufsize=1, universal_newlines=True)
# p = Popen(["echo", "hello world"], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)
p = Popen(["cat"], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)

# write
print("hello world\n", file=p.stdin)
p.stdin.flush()

# read
print("output:", p.stdout.readline().rstrip("\n"))

# close
p.stdin.close()
p.stdout.close()
p.wait()

# p.stdin.write("a\n")
# p.stdin.close()

# with p.stdout as output:
#   print(output.readline())

# # print("readline:", p.stdout.readline())

# # print(p.stdout.read())

# print("poll:", p.poll())



# for command in commandlist:
#     print('From PIPE: Q:', child.stdout.readline().rstrip('\n'))
#     print(command, file=child.stdin)
#     #XXX you might need it to workaround bugs in `subprocess` on Python 3.3
#     #### child.stdin.flush()
#     if command != 'Exit':
#         print('From PIPE: A:', child.stdout.readline().rstrip('\n'))
# child.stdin.close() # no more input
# assert not child.stdout.read() # should be empty
# child.stdout.close()
# child.wait()