#
# NAME
#
#   usage.py
#
# DESCRIPTION
#
#   Wren GUI application's disk and memory usage calculator module. Determines
#   and returns disk and memory usage (in bytes) for a running Wren platform.
#
# AUTHOR
#
#   Originally written by Michael Spencer.
#   Maintained by the Wren GUI project developers.
#
#
# The Wren GUI project; Copyright 2015 the Wren GUI project developers.
# See the COPYRIGHT file in the top-level directory of this distribution
# for individual attributions.
#
# This file is part of the Wren GUI project. It is subject to the license terms
# in the LICENSE file found in the top-level directory of this distribution.
# No part of the Wren GUI project, including this file, may be copied,
# modified, propagated, or distributed except according to the terms contained
# in the LICENSE file.
#
# This program comes with ABSOLUTELY NO WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# LICENSE file found in the top-level directory of this distribution for
# more details.
#

from lib.pipechain import PipeChain
from lib.paths import PATH_MOUNT_DIR

class UsageResult:
  total = ''
  used = ''
  free = ''

  def __init__(self, total_used_free=None):
    # initialize attributes from bytes list [total, used, free]
    if total_used_free != None:
      self.total, self.used, self.free = total_used_free

  def __repr__(self):
    # string representation for debugging
    return 'Total:%s Used:%s Free:%s' % (self.total, self.used, self.free)


class MemoryUsage:

  def __init__(self):
    attrs = [['ram', 'Mem'],
             ['swap', 'Swap'],
             ['total', 'Total']]

    # define grep pattern for command filtering
    grep_str = ''
    for attr in attrs:
      if not grep_str:
        grep_str += '^\(%s' % attr[1] 
      else:
        grep_str += '\|%s' % attr[1]
    grep_str += '\):'

    # define commands
    usage_commands=[['free', '-bt'],
                   ['grep', grep_str],
                   ['tr', '-s', ' '],
                   ['cut', '-d', ' ', '-f', '1-4']]

    # pipe commands and store output
    usage_output = PipeChain(usage_commands).output

    # filter each stat into associated lists
    for attr in attrs:
      values = PipeChain([
          ['echo', usage_output],
          ['grep', '^%s:' % attr[1]],
          ['cut', '-d', ' ', '-f', '2-4']
        ]).output.strip().split()

      # convert strings to numbers and store
      if len(values) > 0:
        for i,v in enumerate(values):
          try:
            values[i] = long(v)
          except ValueError:
            pass
        setattr(self, attr[0], UsageResult(values))
      else:
        setattr(self, attr[0], UsageResult())


class DiskUsage:

  def __init__(self):
    attrs = [['device', '00-device'],
             ['save', '04-save']]

    # define grep pattern for command filtering
    grep_str = ''
    for attr in attrs:
      if not grep_str:
        grep_str += ' %s\/\(%s' % (PATH_MOUNT_DIR, attr[1]) 
      else:
        grep_str += '\|%s' % attr[1]
    grep_str += '\)$'

    # define commands
    usage_commands=[['df', '-B1'],
                   ['grep', grep_str],
                   ['tr', '-s', ' '],
                   ['cut', '-d', ' ', '-f', '2-']]

    # pipe commands and store output
    usage_output = PipeChain(usage_commands).output

    # filter each stat into associated lists
    for attr in attrs:
      values = PipeChain([
          ['echo', usage_output],
          ['grep', '\/%s$' % attr[1]],
          ['cut', '-d', ' ', '-f', '1-3']
        ]).output.strip().split()

      # convert strings to numbers and store
      if len(values) > 0:
        for i,v in enumerate(values):
          try:
            values[i] = long(v)
          except ValueError:
            pass
        setattr(self, attr[0], UsageResult(values))
      else:
        setattr(self, attr[0], UsageResult())


def bytes_to_human(byte_count, max_size=None):
  # format byte count to human readable size
  # max_size (char, optional) determines the highest division
  result = long(byte_count)
  size = 'B'
  for i,v in enumerate(['K', 'M', 'G', 'T', 'P']):
    if long(round(result, 0)) >= 1024:
      result = round(float(byte_count) / pow(1024, i+1), 1)
      size = v
    else:
      break
    if size == max_size:
      break
  if size in ['B', 'K', 'M']:
    format_str = '{:.0f}'
  else:
    format_str = '{:.1f}'
  result = format_str.format(result) + size
  return result
