#
# NAME
#
#   operationglade.py
#
# DESCRIPTION
#
#   Wren GUI application's operation interface management file. Loads the
#   operation glade interface, handles associated signals, and provides
#   status messaging to the user.
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

import traceback
from gi.repository import Gtk, Gdk
from lib.operation import Operation
from lib.paths import PATH_OPERATION_GLADE

class OperationGlade:

  def __init__(self, title, parent_window, close_callback=None,
               autoscroll=True, shell=False):
    self.title = title
    self.parent_window = parent_window
    self.autoscroll = autoscroll
    self.shell=shell

    self.done = False

    # load operation glade window and connect signals
    builder = self.builder = Gtk.Builder()
    builder.add_from_file(PATH_OPERATION_GLADE)
    builder.connect_signals(self)

    # reference window and required child elements
    window = self.window = builder.get_object('window1')
    self.label_status = builder.get_object('label_status')
    self.expander = builder.get_object('expander1')
    self.textview = builder.get_object('textview_output')
    self.scrolledwindow = builder.get_object('scrolledwindow_output')
    self.button_close = builder.get_object('button_close')

    # set window title
    if title is not None:
      window.set_title(title)

    # set window as overlay of parent window
    if parent_window is not None:
      window.set_transient_for(parent_window)

    # Disable button_close
    self._disable_close()

  ### SIGNALS

  def on_window1_delete_event(self, widget, data=None):
    # Disable window close button until button_close is enabled
    return not self.done

  def on_window1_key_press_event(self, widget, event):
    # close window when escape key is pressed (if operation is done)
    if event.keyval == Gdk.KEY_Escape and self.done:
      self.window.destroy()

  def on_button_close_clicked(self, widget, data=None):
    # close window when button_close clicked if operation is done
    if self.done:
      self.window.destroy()

  def on_textview_output_size_allocate(self, widget, data=None):
    # Scroll to bottom on textview expansion
    self.scroll()

  def on_expander1_activate(self, widget, data=None):
    # Scroll to bottom when textview is expanded
    self.scroll()

  ### METHODS

  def show(self):
    self.window.show()

  def expand(self, expanded=True):
    self.expander.set_expanded(expanded)

  def collapse(self):
    self.expand(False)

  def scroll(self, force=False):
    # scroll to bottom if autoscroll is enabled or force is True
    if self.autoscroll is True or force is True:
      adj = self.scrolledwindow.get_vadjustment()
      adj.set_value(adj.get_upper() - adj.get_page_size())

  def run_command(self, command, shell=False):
    self.done = False

    # disable closing the window until operation completes
    self._disable_close()
    
    # initialize subprocess operation
    operation = Operation(done_callback=self.done_callback,
                          output_callback=self.output_callback)

    # run subprocess operation
    try:
      operation.run(command, shell=shell)
      self._set_message_working()
    except:
      # on (python-level) failure, display error and allow window to be closed
      self.done = True
      self._enable_close()
      self._set_message_error()
      strerror = traceback.format_exc()
      print(strerror)
      self.output_callback(strerror)
      self.expand()
      self.scroll(force=True)

  def done_callback(self, returncode):
    self.done = True

    # allow window to be closed
    self._enable_close()
    
    if returncode == 0:
      # status: success - display message
      self._set_message_complete()
    elif returncode is None:
      # status: unknown - display message and expand terminal output
      self._set_message_complete_unknown()
      self.expand()
      self.scroll(force=True)
    else:
      # status: error - display message and expand terminal output
      self._set_message_error()
      self.expand()
      self.scroll(force=True)

  def output_callback(self, output):
    # Print output to textview
    buf = self.textview.get_buffer()
    buf.insert_at_cursor(output)

  def _enable_close(self, enabled=True):
    self.button_close.set_sensitive(enabled)

  def _disable_close(self):
    self._enable_close(False)

  def _set_message_working(self):
    self.label_status.set_markup('<i>Working...</i>')

  def _set_message_complete(self):
    self.label_status.set_markup(
      '<span foreground="#009900">'
      'Complete.'
      '</span>')

  def _set_message_error(self):
    self.label_status.set_markup(
      '<span foreground="#aa0000"><i>'
      'An error occured.'
      '</i></span>')

  def _set_message_complete_unknown(self):
    self.label_status.set_markup(
      '<span foreground="#aa0000"><i>'
      'Complete - status unknown... confirm output.'
      '</i></span>')
