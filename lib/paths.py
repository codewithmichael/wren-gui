#
# NAME
#
#   paths.py
#
# DESCRIPTION
#
#   Wren GUI application's system path constants file.
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

import sys

PATH_PLATFORMUTIL_SH = '%s/lib/platformutil.sh' % sys.path[0]
PATH_MAIN_GLADE = '%s/lib/main.glade' % sys.path[0]
PATH_ABOUT_GLADE = '%s/lib/about.glade' % sys.path[0]
PATH_OPERATION_GLADE = '%s/lib/operation.glade' % sys.path[0]
PATH_SAVE_GLADE = '%s/lib/save.glade' % sys.path[0]

PATH_MOUNT_DIR = '/mnt/wren'
