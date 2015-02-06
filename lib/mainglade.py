#
# NAME
#
#   mainglade.py
#
# DESCRIPTION
#
#   Wren GUI application's primary interface management file. Loads the main
#   glade interface, handles associated signals, and fires off requested
#   operations.
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

from __future__ import print_function
from gi.repository import Gtk, GObject
from lib.usage import bytes_to_human
from lib.operationglade import OperationGlade
from lib.saveglade import SaveGlade
from lib.paths import PATH_PLATFORMUTIL_SH, PATH_MAIN_GLADE, PATH_ABOUT_GLADE

class MainGlade:

  def __init__(self):
    # load "main" and "about" glades and connect signals
    builder = self.builder = Gtk.Builder()
    builder.add_from_file(PATH_MAIN_GLADE)
    builder.add_from_file(PATH_ABOUT_GLADE)
    builder.connect_signals(self)

    # initialize empty module references
    self.operation_glade = None
    self.save_glade = None

    # reference window elements
    window = self.window = builder.get_object('window1')
    about_dialog = self.about_dialog = self.builder.get_object('aboutdialog1')
    about_dialog.set_transient_for(window)

    # reference stat labels (for updates)
    for i in ['ram', 'swap', 'memory', 'device', 'save']:
      for j in ['total', 'used', 'free']:
        label_name = 'label_%s_%s' % (i, j)
        setattr(self, label_name, builder.get_object(label_name))

    # reference "uncompressed save" label
    self.label_uncompressed_save=builder.get_object('label_uncompressed_save')

    # reference "memory free after save" label (for updates)
    self.label_memory_free_after_save = \
      builder.get_object('label_memory_free_after_save')

    # reference menu items (for enable/disable)
    self.menu_save = \
      builder.get_object('menu_save')
    self.menu_increase_save_size = \
      builder.get_object('menu_increase_save_size')
    self.menu_grub = \
      builder.get_object('menu_grub')

  ### SIGNALS

  def on_window1_destroy(self, window, data=None):
    Gtk.main_quit()

  def on_menu_quit_activate(self, menuitem, data=None):
    Gtk.main_quit()

  def on_menu_save_activate(self, menuitem, data=None):
    self.run_operation_save()

  def on_menu_update_grub_activate(self, menuitem, data=None):
    self.run_operation_update_grub()

  def on_menu_increase_save_size_activate(self, menuitem, data=None):
    self.run_operation_increase_save_size()

  def on_menu_delete_apt_caches_activate(self, menuitem, data=None):
    self.run_operation_delete_apt_caches()

  def on_menu_drop_caches_activate(self, menuitem, data=None):
    self.run_operation_drop_caches()

  def on_menu_view_grub_config_activate(self, menuitem, data=None):
    self.run_operation_view_grub_config()

  def on_menu_preview_updated_grub_config_activate(self, menuitem, data=None):
    self.run_operation_preview_updated_grub_config()

  def on_menu_about_activate(self, menuitem, data=None):
    self.about_dialog.run()
    self.about_dialog.hide()

  ### METHODS

  def set_usage(self, memory_usage=None, disk_usage=None,
                uncompressed_save_bytes=None):

    # update disk stats
    if disk_usage != None:
      self.set_disk_usage(disk_usage)
    # update uncompressed save
    if (uncompressed_save_bytes != None):
      self.set_disk_uncompressed_save(uncompressed_save_bytes)
    # update memory stats
    if memory_usage != None:
      self.set_memory_usage(memory_usage)
    # update memory free after save
    if memory_usage != None and disk_usage != None:
      self.set_memory_free_after_save(memory_usage.total.free,
                                      disk_usage.save.free)

  def set_memory_usage(self, memory_usage):
    self.set_memory_ram(memory_usage.ram)
    self.set_memory_swap(memory_usage.swap)
    self.set_memory_total(memory_usage.total)

  def set_disk_usage(self, disk_usage):
    self.set_disk_device(disk_usage.device)
    self.set_disk_save(disk_usage.save)

  def set_memory_ram(self, usage_result):
    # update stat labels
    self._set_label_bytes(self.label_ram_total, usage_result.total)
    self._set_label_bytes(self.label_ram_used,  usage_result.used)
    self._set_label_bytes(self.label_ram_free,  usage_result.free)

  def set_memory_swap(self, usage_result):
    # update stat labels
    self._set_label_bytes(self.label_swap_total, usage_result.total)
    self._set_label_bytes(self.label_swap_used,  usage_result.used)
    self._set_label_bytes(self.label_swap_free,  usage_result.free)

  def set_memory_total(self, usage_result):
    # update stat labels
    self._set_label_bytes(self.label_memory_total, usage_result.total)
    self._set_label_bytes(self.label_memory_used,  usage_result.used)
    self._set_label_bytes(self.label_memory_free,  usage_result.free)

  def set_disk_device(self, usage_result):
    # update stat labels
    self._set_label_bytes(self.label_device_total, usage_result.total)
    self._set_label_bytes(self.label_device_used,  usage_result.used)
    self._set_label_bytes(self.label_device_free,  usage_result.free)

    # enable/disable menus depending on disk availability
    enable_menu_save = False
    if usage_result.total:
      try:
        long(usage_result.total)
        enable_menu_save = True
      except ValueError:
        pass
    self.menu_save.set_sensitive(enable_menu_save)
    self.menu_grub.set_sensitive(enable_menu_save)

  def set_disk_save(self, usage_result):
    # update stat labels
    self._set_label_bytes(self.label_save_total, usage_result.total)
    self._set_label_bytes(self.label_save_used,  usage_result.used)

    # update free label with color and tooltip
    tooltip = None
    color = None
    try:
      if long(usage_result.free) < 500*pow(1024, 2):
        tooltip = ('You have less than 500 MiB of active save space. Consider '
                  'increasing save size.')
        color = '#aa0000'
    except ValueError:
      pass
    self._set_label_bytes(self.label_save_free,  usage_result.free,
                          tooltip=tooltip, color=color)

  def set_disk_uncompressed_save(self, uncompressed_save_bytes):
    try:
      self._set_label_bytes(self.label_uncompressed_save,
                            long(uncompressed_save_bytes))
      
    except ValueError:
      self._set_label_bytes(self.label_uncompressed_save, '')

  def set_memory_free_after_save(self, memory_free_bytes, save_free_bytes):
    enable_menu_increase_save_size = False

    # update memory free after save label with color and tooltip
    try:
      memory_free = long(memory_free_bytes) - long(save_free_bytes)
      if memory_free < 0:
        memory_free = 0
      tooltip = None
      color = None
      if memory_free < pow(1024, 3):
        tooltip = 'Save size increase requires 1G. Try dropping memory caches.'
        color = '#aa0000'
      else:
        enable_menu_increase_save_size = True
      self._set_label_bytes(self.label_memory_free_after_save, memory_free,
                            tooltip=tooltip, color=color)
    except ValueError:
      self._set_label_bytes(self.label_memory_free_after_save, '')

    # enable/disable menus depending on memory availability
    self.menu_increase_save_size.set_sensitive(enable_menu_increase_save_size)

  def run_operation_save(self):
    # initialize save name selection dialog with callback
    save_glade = self.save_glade = \
      SaveGlade('Save to Disk', self.window,
                ok_callback=self._save_ok_callback)
    save_glade.show()

  def _save_ok_callback(self, save_name):
    # perform save to disk action
    self.save_glade = None
    self._run_operation('Save to Disk (save name: %s)' % save_name,
                        [PATH_PLATFORMUTIL_SH, 'save', save_name],
                        expanded=True)

  def run_operation_increase_save_size(self):
    # initialize warning dialog
    dialog = Gtk.MessageDialog(self.window,
                               Gtk.DialogFlags.DESTROY_WITH_PARENT,
                               Gtk.MessageType.WARNING,
                               Gtk.ButtonsType.OK_CANCEL,
                               'Increase Save Size?')
    dialog.format_secondary_text('Increasing your active save size provides '
                                 'additional room in RAM for your active save '
                                 'data. This does not directly affect the '
                                 'size of your save file, but does allow for '
                                 'it to grow larger if you perform a '
                                 'subsequent save operation.'
                                 "\n\n"
                                 'Note that you MUST have at least 1 GiB of '
                                 'RAM free ON TOP OF your existing active data '
                                 'limit to perform this operation, otherwise a '
                                 'memory overflow and system deadlock could '
                                 'occur. See "Available memory after active '
                                 'data limit" at the bottom of the main '
                                 'display to verify this value.')
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
      # perform increase save size action
      self._run_operation('Increase Save Size',
                          [PATH_PLATFORMUTIL_SH, 'increasesavesize'])

    dialog.destroy()

  def run_operation_delete_apt_caches(self):
    # initialize warning dialog
    dialog = Gtk.MessageDialog(self.window,
                               Gtk.DialogFlags.DESTROY_WITH_PARENT,
                               Gtk.MessageType.WARNING,
                               Gtk.ButtonsType.OK_CANCEL,
                               'Delete Apt Caches?')
    dialog.format_secondary_text('This will remove all cached package '
                                 'installation files from your system. If you '
                                 'wish to reinstall or reconfigure these '
                                 'packages, they will have to be downloaded '
                                 'again.')
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
      # perform delete apt caches action
      self._run_operation('Delete Apt Caches', ['apt-get', 'clean'])

    dialog.destroy()

  def run_operation_drop_caches(self):
    # initialize warning dialog
    dialog = Gtk.MessageDialog(self.window,
                               Gtk.DialogFlags.DESTROY_WITH_PARENT,
                               Gtk.MessageType.WARNING,
                               Gtk.ButtonsType.OK_CANCEL,
                               'Drop Memory Caches?')
    dialog.format_secondary_text('This will remove clean '
                                 'page/buffer/inode/dentry cached entries '
                                 'from RAM.'
                                 "\n\n"
                                 'This is a safe operation, but may '
                                 'temporarily slow certain systems, as these '
                                 'entries mostly exist to cache common or '
                                 'recently accessed files from disk.'
                                 "\n\n"
                                 'However, the cache is also used to house '
                                 'temporary file systems. It can be useful '
                                 'to clean them to allow for more up-front '
                                 'tmpfs storage (like active save data).')
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
      # perform drop memory caches action
      self._run_operation('Drop Memory Caches',
                          'sync; echo 3 >/proc/sys/vm/drop_caches',
                          shell=True)

    dialog.destroy()

  def run_operation_view_grub_config(self):
    # open grub config for viewing
    self._run_operation('View Current Grub Config',
                        [PATH_PLATFORMUTIL_SH, 'viewgrubconfig'],
                        expanded=True,
                        autoscroll=False)

  def run_operation_preview_updated_grub_config(self):
    # display preview of updated grub config
    self._run_operation('Preview Updated Grub Config',
                        [PATH_PLATFORMUTIL_SH, 'previewgrubconfig'],
                        expanded=True,
                        autoscroll=False)

  def run_operation_update_grub(self):
    # initialize warning dialog
    dialog = Gtk.MessageDialog(self.window,
                               Gtk.DialogFlags.DESTROY_WITH_PARENT,
                               Gtk.MessageType.WARNING,
                               Gtk.ButtonsType.OK_CANCEL,
                               'Update Grub Config?')
    dialog.format_secondary_text('This will overwrite your existing Grub '
                                 'configuration file. A backup will be '
                                 'created as part of this operation, but '
                                 'updating will have important ramifications '
                                 'if you have created custom boot entries or '
                                 'made any manual entry modifications (they '
                                 'will be replaced/removed).'
                                 "\n\n"
                                 'It is recommended you first run the "View '
                                 'Current Grub Config" and "Preview Updated '
                                 'Grub Config" options to verify the changes '
                                 'before proceeding.'
                                 "\n\n"
                                 'If you require a custom Grub configuration, '
                                 'it may be preferable to copy the output '
                                 'from "Preview Updated Grub Config" and '
                                 'perform the updates manually.')
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
      # perform grub configuration update
      self._run_operation('Updated Grub Config',
                          [PATH_PLATFORMUTIL_SH, 'updategrub'])

    dialog.destroy()

  def _run_operation(self, title, command, expanded=False, autoscroll=True,
                     shell=False):

    # initialize subprocess operation window with defined options
    operation_glade = self.operation_glade = \
      OperationGlade(title, self.window,
                     close_callback=self._operation_close_callback,
                     autoscroll=autoscroll)

    # expand terminal output display if requested
    if expanded is True:
      operation_glade.expand()

    operation_glade.show()

    # wait for window to show and then run command
    GObject.timeout_add_seconds(0.5,
      lambda: operation_glade.run_command(command, shell=shell))

  def _operation_close_callback(self):
    self.operation_glade = None

  def _set_label_bytes(self, label, byte_count, tooltip=None, color=None):
    # convert bytes to human-readable format
    value = None
    tooltip_value = tooltip
    try:
      value = bytes_to_human(byte_count)
      if tooltip_value == None:
        tooltip_value = bytes_to_human(byte_count, 'M')
    except:
      pass

    # convert empty value for display
    if value == None:
      value = '---'

    # set text with (optional) requested color
    if color == None:
      label.set_text(value)
    else:
      label.set_markup('<span foreground="%s">%s</span>' %(color, value))

    # set tooltip
    if tooltip_value == None:
      label.set_has_tooltip(False)
    else:
      label.set_tooltip_text(tooltip_value)
