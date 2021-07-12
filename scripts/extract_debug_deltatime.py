import sys
import getopt
import re
from tqdm import tqdm

"""
ABSTRACT

This script extract deltatime information from debug logs using
`DebugAttemptEquation` and `DebugApplyEquation`. The debugging items have three
forms (in order of log appearance):
1. DebugAttemptEquation: Log attempt to apply equation `E` on term `T`
2. DebugAttemptEquation: Log result of `attemptEquation` (whether "equation is
    applicable" or "equation is not applicable"): tries to match/unify with `T`
    and if it succeeds, then checks if the  `requires` clause is satisfied
    (whether or not it's applicable).
3. DebugApplyEquation: Log result of applying equation
"""


def debug(msg):
  print("[>] {0}".format(msg))

#
# command line options
#


msg_usage = """
usage:
> python3 extract_debug_deltatime.py <input_file>  
"""

args = sys.argv[1:]
input_filename = None

if len(args) != 1:  # error
  raise Exception("incorrect usage" + msg_usage)
elif args[0] in ["-h", "--help"]:  # help
  print(msg_usage)
else:  # input
  input_filename = args[0]

#
# Interpret
#

items = []
item_info_cache = ""


def newItem():
  return {
      "name":          None,  # [DebugAttemptEquation|DebugApplyEquation]
      "step":          None,  # [1|2|3]
      "applicability": None,  # equation applicability
      "timestamp":     None,  # kore-exec timestamp
      "info":          None   # text associated with debug item
  }


def commitItem():  # Commit current item and append a new blank item
  global items, item_info_cache
  if 0 < len(items):
    items[-1]["info"] = item_info_cache
    item_info_cache = ""
  items.append(newItem())


# Regex pattern for a Header
pat_Header = re.compile(
    'kore-exec: \\[(\\d+)\\] Debug \\((DebugAttemptEquation|DebugApplyEquation)\\)')


def isHeader(line):  # Check if a line is a Header
  return pat_Header.search(line) is not None


pat_DebugAttemptEquation = re.compile("DebugAttemptEquation")
pat_DebugApplyEquation = re.compile("DebugApplyEquation")


def extractName(line):  # Extract name from Header
  if pat_DebugAttemptEquation.search(line) is not None:
    return "DebugAttemptEquation"
  elif pat_DebugApplyEquation.search(line) is not None:
    return "DebugApplyEquation"
  else:
    raise Exception("bad when extracting name from '{0}'".format(line))


def extractTimestamp(line):  # Extract timestamp from Header
  strs = re.split(r'[\[\]]+', line)
  if 2 <= len(strs):
    return int(strs[1]) / 1000000  # Convert musec (10e-6) to sec (10e0)
  else:
    raise Exception("bad when extracting timestamp from '{0}'".format(line))


pat_step1 = re.compile('applying equation')
pat_step2S = re.compile('equation is applicable')
pat_step2F = re.compile('equation is not applicable')
pat_step3 = re.compile('applied equation')


def extractStep(line):  # Extract step from info line (if possible)
  if pat_step1.search(line) is not None:
    return
  elif pat_step2F.search(line) is not None:
    return 2
  elif pat_step2F.search(line) is not None:
    return 2
  elif pat_step3.search(line) is not None:
    return 3
  else:
    return None


def extractApplicable(line):  # Extract if equation is applicable
  if pat_step2S.search(line) is not None:
    return True
  elif pat_step2S.search(line) is not None:
    return False


# Produce items
print("interpreting input file")
with open(input_filename, "r+") as input_file:
  for line in tqdm(input_file):
    # Figure out what kind of line it is
    if isHeader(line):  # Is a Header
      commitItem()
      items[-1]["name"] = extractName(line)
      items[-1]["timestamp"] = extractTimestamp(line)
      items[-1]["step"] = 1
    else:  # Is an info line
      step = extractStep(line)
      if step is not None:
        items[-1]["step"] = step

      applicability = extractApplicable(line)
      if applicability is not None:
        items[-1]["applicability"] = applicability

      item_info_cache += "{0}\n".format(line)

#
# Calculate
#


def calculateDeltaTimes():
  print("Calculating deltatimes")

  deltatimes = []
  attempts_applicable = 0
  attempts_unapplicable = 0

  step = None
  item_steps = None

  def reset():
    nonlocal step, item_steps
    step = 1
    item_steps = [None, None, None]

  reset()  # initialize

  for item in tqdm(items):

    if step == item["step"]:  # Is expected next step
      item_steps[step - 1] = item

      if step == 1:
        step += 1

      # If equation was found not applicable
      elif step == 2 and not item["applicability"]:
        [item1, item2, _] = item_steps
        dt12 = item2["timestamp"] - item1["timestamp"]  # dt step 1 -> 2
        deltatimes.append((False, [dt12, item2["info"]]))
        attempts_unapplicable += 1
        reset()

      # After application of equation
      elif step == 3:
        [item1, item2, item3] = item_steps
        dt12 = item2["timestamp"] - item1["timestamp"]  # dt step 1 -> 2
        dt23 = item3["timestamp"] - item2["timestamp"]  # dt step 2 -> 3
        dt13 = dt12 + dt23  # dt step 1 -> 3 (total)
        deltatimes.append((True, [dt12, dt23, dt13]))
        attempts_applicable += 1
        reset()

  attempts_total = attempts_applicable + attempts_unapplicable
  debug(
      """unapplicable attempts: {0}
      applicable attempts: {1}
      ------------------------------------------
           total attempts: {2}
  """.format(attempts_unapplicable, attempts_applicable, attempts_total))

  # each element has one of these forms:
  # - (True,  [dt12, dt23, dt13])
  # - (False, [dt])
  return deltatimes


deltatimes = calculateDeltaTimes()

# debug([item["step"] for item in items])
# for item in items[0:5]:
#   debug(item)

# debug(deltatimes[0])
# for dt in deltatimes:
#   debug(dt[2])

# # ! OLD
# i = 0
# while i < len(items) - 2:
#   item1 = items[i]
#   if item1["step"] == 1:
#     item2 = items[i + 1]
#     if item2["step"] == 2:
#       item3 = items[i + 2]
#       if item3["step"] == 3:
#         # Only capture sequence of items that do all three steps consecutively
#         # A failure will happen at step 2, so there will never be a false negative
#         dt12 = item2["timestamp"] - item1["timestamp"]  # dt step 1 -> 2
#         dt23 = item3["timestamp"] - item2["timestamp"]  # dt step 2 -> 3
#         dt13 = dt12 + dt23  # dt step 1 -> 3 (total)
#         deltatimes.append((dt12, dt23, dt13))
#         i += 3
#   i += 1
#   continue

#
# Output
#

DO_WRITE_OUTPUT = True


if DO_WRITE_OUTPUT:

  output_str = ""
  for (applicability, data) in deltatimes:
    if not applicability:
      [dt12, info] = data
      if 100 < dt12:
        output_str += "finds unnapplicable in {0:.4f} sec\n{1}...\n\n".format(
            dt12, info[0:1000])

  # Write output
  debug("Writing deltatimes output to file: " +
        input_filename + ".unapplicable")
  with open(input_filename + ".unapplicable", "w+") as output_file:
    output_file.write(output_str)

# if DO_WRITE_OUTPUT:

#   # Generate deltatimes output string
#   deltatimes_str = ""
#   # TODO: bug, because `deltatimes_str` is empty.... probably `deltatimes` is empty?
#   for (applicability, data) in deltatimes:
#     if applicability:
#       [dt12, dt23, dt13] = data
#       deltatimes_str += "{:.4f}\n".format(dt13)
#     else:
#       [dt12, info] = data
#       deltatimes_str += "UNAPPLICABLE: {:.4f}\n".format(dt12)

  # # Write output
  # debug("Writing deltatimes output to file: " + input_filename + ".deltatime")
  # with open(input_filename + ".deltatime", "w+") as output_file:
  #   output_file.write(deltatimes_str)

  # # Write output
  # with open(output_filename, "w+") as output_file:
  #   output_str = ""
  #   for line in output_lines:
  #     output_str += "\n" + line
  #   output_file.write(output_str)
