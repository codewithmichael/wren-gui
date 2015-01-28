#
# NAME
#
#   saveglade.py
#
# DESCRIPTION
#
#   Wren GUI application's save name selection interface management file. Loads
#   the save glade interface, determines existing save names, handles
#   associated window signals, and returns the selected/provided save name.
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

from gi.repository import Gtk, Gdk
from subprocess import CalledProcessError, check_output
from lib.operationglade import OperationGlade
from lib.paths import PATH_PLATFORMUTIL_SH, PATH_SAVE_GLADE

class SaveGlade:

  def __init__(self, title, parent_window, ok_callback, cancel_callback=None):
    self.parent_window = parent_window
    self.ok_callback = ok_callback
    self.cancel_callback = cancel_callback

    # load save glade and connect signals
    builder = self.builder = Gtk.Builder()
    builder.add_from_file(PATH_SAVE_GLADE)
    builder.connect_signals(self)

    # reference window and required child elements
    window = self.window = builder.get_object('window1')
    comboboxtext = self.comboboxtext = builder.get_object('comboboxtext1')
    comboboxtext_entry = self.comboboxtext_entry = \
      Gtk.Bin.get_child(comboboxtext)
    button_ok = self.button_ok = builder.get_object('button_ok')

    # set window title
    if title is not None:
      window.set_title(title)

    # set window as overlay of parent window
    if parent_window is not None:
      window.set_transient_for(parent_window)

    # prepare save names combobox
    comboboxtext.set_entry_text_column(0)

    # load existing save names
    save_names = []
    try:
      save_names = check_output([PATH_PLATFORMUTIL_SH, 'getsavenames'])\
        .strip().split('\n')
    except CalledProcessError:
      pass

    # load current save name (from boot or platform)
    save_name = ''
    save_name_index = -1
    try:
      save_name = check_output([PATH_PLATFORMUTIL_SH, 'getsavename']).strip()
      save_name_index = save_names.index(save_name)
    except CalledProcessError:
      pass
    except ValueError:
      pass

    # add save names to combobox
    for value in save_names:
      comboboxtext.append_text(value)

    # populate editable entry
    if save_name_index >= 0:
      comboboxtext.set_active(save_name_index)
    elif save_name:
      comboboxtext_entry.set_text(save_name)
    else:
      button_ok.set_sensitive(False)


  ### SIGNALS

  def on_window1_key_press_event(self, widget, event):
    # initiate cancel when escape key is pressed
    if event.keyval == Gdk.KEY_Escape:
      self.call_cancel()

  def on_window1_delete_event(self, widget, data=None):
    # initiate cancel when window is closed
    self.call_cancel()

  def on_button_cancel_clicked(self, widget, data=None):
    # initiate cancel when button_cancel is clicked
    self.call_cancel()

  def on_button_ok_clicked(self, widget, data=None):
    # initiate ok callback when button_ok is clicked
    self.call_ok()

  def on_comboboxtext_entry_changed(self, widget, data=None):
    # disable button when editable entry is empty
    self.button_ok.set_sensitive(bool(widget.get_text()))

  ### METHODS

  def show(self):
    self.window.show()

  def call_ok(self):
    # close window and initiate ok_callback with selected save name
    self.window.hide()
    if self.ok_callback is not None:
      self.ok_callback(self.comboboxtext_entry.get_text())
    self.window.destroy()

  def call_cancel(self):
    # close window and initiate cancel_callback
    self.window.destroy()
    if self.cancel_callback is not None:
      self.cancel_callback()
