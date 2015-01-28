#
# NAME
#
#   pipechain.py
#
# DESCRIPTION
#
#   Wren GUI application's multi-piped subprocess module. Accepts a set of
#   commands to run, pipes them into one another, and stores the final output.
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

from subprocess import PIPE, STDOUT, Popen

class PipeChain:

  output     = ''
  returncode = 0

  def __init__(self, commands):
    p_old = None
    p_new = None
    
    # iterate over commands, piping each's stdout into the stdin of the next
    for command in commands:
      p_old = p_new
      if p_old == None:
        p_new = Popen(command, stdout=PIPE)
      else:
        p_new = Popen(command, stdin=p_old.stdout, stdout=PIPE)
        p_old.stdout.close() # allow SIG_PIPE errors to fall through

    # store output of final command
    if p_new != None:
      self.output = p_new.communicate()[0]

