#
# NAME
#
#   operation.py
#
# DESCRIPTION
#
#   Wren GUI application's piped subprocess operations file. Opens and watches
#   a requested subprocess, passing back data and IO signals via designated
#   callback functions.
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
from gi.repository.GObject import IO_IN, IO_HUP, io_add_watch, source_remove

class Operation:

  def __init__(self, done_callback=None, output_callback=None):
    self.done_callback = done_callback
    self.output_callback = output_callback
    self.process = None
    self.io_in_id = None
    self.io_hup_id = None

  def run(self, command, shell=False):
    # disable IO watchers (in case of already running operation)
    self._stop_listening()

    # open subprocess
    process = self.process = Popen(command, stdout=PIPE, stderr=STDOUT,
                                   shell=shell)

    # initialize IO watchers
    self.io_in_id = io_add_watch(process.stdout, IO_IN, self._handle_io)
    self.io_hup_id = io_add_watch(process.stdout, IO_HUP, self._handle_io)

  def _handle_io(self, fd, condition):
    if condition == IO_IN:
      # handle subprocess output
      self._read_to_output(fd)
      return True
    else:
      if condition == IO_HUP:
        # handle hang up (pipe closed)
        # wait for return code
        self.process.wait()
        # disable IO watchers
        self._stop_listening()
        # handle any remaining subprocess output
        self._read_all_to_output(fd)
        # trigger done callback
        if self.done_callback is not None:
          self.done_callback(self.process.returncode)
      # unregister IO watcher (otherwise CPU will spike to near 100%)
      return False

  def _read_to_output(self, fd):
    # if an output callback was defined,
    # pass it a block of available subprocess output
    if self.output_callback is not None:
      data = fd.read(1024)
      if data:
        self.output_callback(data)

  def _read_all_to_output(self, fd):
    # if an output callback was defined,
    # pass it all available subprocess output
    if self.output_callback is not None:
      data = fd.read(1024)
      while data:
        self.output_callback(data)
        data = fd.read(1024)

  def _stop_listening(self):
    # disable IO watchers
    if self.io_in_id is not None:
      source_remove(self.io_in_id)
      self.io_in_id = None
    if self.io_hup_id is not None:
      source_remove(self.io_hup_id)
      self.io_hup_id = None
