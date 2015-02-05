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

# ensure platform name is defined
test x"$RUN_ENV_PLATFORM_NAME" = x \
  && { echo "Could not determine platform environment name - exiting..." >&2 ; exit 1 ; }

# load platform environment
. "/etc/$RUN_ENV_PLATFORM_NAME/platform-env" \
    || { echo "Could not load platform environment - exiting..." >&2 ; exit 1 ; }


# Define paths
path_active_save="/mnt/$RUN_ENV_PLATFORM_NAME/04-save"
path_grub_config="/mnt/$RUN_ENV_PLATFORM_NAME/00-device/boot/grub/grub.cfg"
bin_save="/etc/$RUN_ENV_PLATFORM_NAME/save.sh"
bin_updategrub="/etc/$RUN_ENV_PLATFORM_NAME/update-grub.sh"
bin_increasesavesize="/etc/$RUN_ENV_PLATFORM_NAME/increase-save-size.sh"


# error handler with graceful exit
errorExit()
{
  test x"$1" = x \
    && echo "An error occurred - exiting..." >&2 \
    || echo "$1 - exiting..." >&2

  exit 1
}


# ensure root permission
testRootUser || errorExit "Root permission required"

# ensure operation request
test x"$1" != x \
  && operation="$1" \
  || errorExit "No operation requested"

# load boot configuration and options
loadRunEnvConf || errorExit
updateBootOptions || errorExit

# handle requested action
case "$operation" in

  getsavename )             # return the appropriate save name for saving
                            if test x"$BOOT_SAVE" != x; then
                              echo "$BOOT_SAVE"
                            elif test x"$PLATFORM_DEFAULT_SAVE" != x; then
                              echo "$PLATFORM_DEFAULT_SAVE"
                            else
                              errorExit "Unable to determine save name"
                            fi
                            ;;

  getsavenames )            # return all existing save names
                            path_dir_saves=`getDeviceSavesDirectoryPath` \
                              && test x"$path_dir_saves" != x \
                              || errorExit "Unable to determine device save storage directory"
                            if test -d "$path_dir_saves"; then
                              saves=`getAbsoluteDirectoryList "$path_dir_saves"` \
                                || errorExit "Unable to load save storage directory content"
                              while IFS= read -r i; do
                                test -d "$i" && echo `basename "$i"`
                              done <<EOF
$saves
EOF
                            fi
                            ;;

  getuncompressedsavesize ) # return the uncompressed file size of the active save data
                            du -xa -B1 -d0 "$path_active_save" | cut -f1 \
                              || errorExit "Unable to determine uncompressed save size"
                            ;;

  increasesavesize )        # increase the active save data size in memory
                            $bin_increasesavesize || exit $?
                            ;;

  save )                    # save to disk using the provided save name
                            test x"$2" != x \
                              && save_name="$2" \
                              || errorExit "Save name required"
                            $bin_save -s "$save_name" || exit $?
                            ;;

  viewgrubconfig )          # view current grub configuration
                            test -f "$path_grub_config" \
                              && cat "$path_grub_config" \
                              || errorExit "Grub configuration file not found"
                            ;;

  previewgrubconfig )       # preview an updated grub configuration
                            $bin_updategrub || exit $?
                            ;;

  updategrub )              # update the current grub configuration
                            echo "Verifying Grub configuration directory..."
                            dir_grub_config=`dirname "$path_grub_config"` \
                              && test -d "$dir_grub_config" \
                              || errorExit "Grub configuration directory not found"
                            echo "Generating updated Grub configuration..."
                            updated_grub_config=`$bin_updategrub` \
                              || errorExit "Unable to generate updated Grub configuration"
                            if test -f "$path_grub_config"; then
                              echo "Backing up current Grub configuration..."
                              echo "- Copying to: $path_grub_config~"
                              cp "$path_grub_config" "$path_grub_config~" \
                                || errorExit "Unable to copy to: $path_grub_config~"
                            fi
                            echo "Updating Grub configuration..."
                            echo "- Writing to: $path_grub_config"
                            echo "$updated_grub_config" >"$path_grub_config" \
                              || errorExit "Error writing to file: $path_grub_config"
                            echo "Done."
                            ;;

  * )                       # fail (invalid operation)
                            errorExit "Invalid operation requested: \"$operation\""
                            ;;
esac
