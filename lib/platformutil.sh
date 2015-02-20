#!/bin/sh
#
# NAME
#
#   platformutil.sh
#
# DESCRIPTION
#
#   Wren GUI application's shell utility file. Performs all interaction with
#   Wren platform applications as is required by Wren GUI.
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

# clean environment
unset IFS
PATH=/usr/sbin:/usr/bin:/sbin:/bin

# error handler with graceful exit
errorExit()
{
  test x"$1" = x \
    && echo "An error occurred - exiting..." >&2 \
    || echo "$1 - exiting..." >&2

  exit 1
}

# ensure root permission
test x"$(id -u)" = x0 || errorExit "Root permission required"

# ensure operation request
test x"$1" != x \
  && operation="$1" \
  || errorExit "No operation requested"

# handle requested action
case "$operation" in

  getsavename )         # return the appropriate save name for saving
                        wren status savename || exit $?
                        ;;

  getsavenames )        # return all existing save names
                        wren status savenames || exit $?
                        ;;

  increasesavesize )    # increase the active save data size in memory
                        wren +active --force -v || exit $?
                        ;;

  save )                # save to disk using the provided save name
                        test x"$2" != x \
                          || errorExit "Save name required"
                        wren set savename "$2" || exit $?
                        wren save || exit $?
                        ;;

  viewgrubconfig )      # view current grub configuration
                        wren grub show || exit $?
                        ;;

  previewgrubconfig )   # preview an updated grub configuration
                        wren grub generate || exit $?
                        ;;

  updategrub )          # update the current grub configuration
                        wren grub write -v || exit $?
                        ;;

  * )                   # fail (invalid operation)
                        errorExit "Invalid operation requested: \"$operation\""
                        ;;
esac
