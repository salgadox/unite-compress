import datetime
import logging
import os
import re
import subprocess
import tempfile
from os import path

import magic
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from pytz import timezone

from unite_compress.files.models import ConvertingCommand
from unite_compress.files.settings import CONV_DIR, ORIG_DIR

logger = logging.getLogger(__name__)


def bytes_to_mib(value: int) -> float:
    # 1 bytes = 9.5367431640625E-7 mebibytes
    return value * 9.5367431640625e-7


def assert_settings(required_settings, error_message_prefix=""):
    """
    Checks if each item from `required_settings` is present in Django settings
    """
    not_present = []
    values = {}

    for required_setting in required_settings:
        if not hasattr(settings, required_setting):
            not_present.append(required_setting)
            continue

        values[required_setting] = getattr(settings, required_setting)

    if not_present:
        if not error_message_prefix:
            error_message_prefix = "Required settings not found."

        stringified_not_present = ", ".join(not_present)

        raise ImproperlyConfigured(
            f"{error_message_prefix} Could not find: {stringified_not_present}"
        )

    return values


class Converter:

    emulation = False

    def call_cli(
        self, cmd, cmd_kwargs, storage=None, file_name=None, without_output=False
    ):
        """OS independency invoking of command line interface"""

        def _call_cli(command):
            logger.info("Calling command: %s" % command)
            if self.emulation:
                return logger.debug("Call: %s" % command)

            command_args = command.split()
            if without_output:
                DEVNULL = open(os.devnull, "wb")
                subprocess.run(command_args, stdout=DEVNULL, stderr=DEVNULL)
            else:
                result = subprocess.run(command_args, stdout=subprocess.PIPE)
                return result.stdout

        if storage is None:
            return _call_cli(cmd % cmd_kwargs)
        else:
            dst_ext = path.splitext(cmd_kwargs["output_file"])[1]
            tmp_input_file = tempfile.NamedTemporaryFile()
            with storage.open(file_name, "rb") as src:
                tmp_input_file.write(src.read())
            tmp_output_file = tempfile.NamedTemporaryFile(suffix=dst_ext)

            _cmd_kwargs = cmd_kwargs.copy()
            _cmd_kwargs["input_file"] = tmp_input_file.name
            _cmd_kwargs["output_file"] = tmp_output_file.name
            out = _call_cli(cmd % _cmd_kwargs)

            # close the input temp file
            tmp_input_file.close()

            # reset the file pointer to the beginning of the file
            tmp_output_file.seek(0)

            # write the tmp file to the storage
            # TODO: fix this terrible workaround
            dst_basename = path.splitext(file_name.replace(ORIG_DIR, CONV_DIR))[0]
            dst_filepath = f"{dst_basename}{dst_ext}"
            with storage.open(dst_filepath, "wb") as dst:
                dst.write(tmp_output_file.read())

            # clouse the output temp file
            tmp_output_file.close()

            # return the stdout
            return out

    @staticmethod
    def choose_convert_command(file):
        """Command for file converting by matching with file name"""
        mime_type = magic.from_file(file.filepath, mime=True)
        commands = ConvertingCommand.objects.filter(is_enabled=True)
        for command in commands:
            if re.match(command.mime_regex, mime_type):
                return command
        return

    def convert_file(self, cmd, file):
        file.convert_status = "started"
        file.save()
        # file.convert_extension = cmd.convert_extension
        try:
            if file.is_local:
                storage = None
            else:
                storage = file.file.storage

            cmd_kwargs = {
                "input_file": file.filepath,
                "output_file": file.converted_path,
            }
            # logger.info("Converting file command: %s" % c)
            output = self.call_cli(
                cmd.command, cmd_kwargs, storage=storage, file_name=file.file.name
            )
            logger.info("Converting file result: %s" % output)
        except Exception:
            logger.error("Converting file error", exc_info=True)
            file.convert_status = "error"
            file.last_convert_msg = "Exception while converting"
            file.save()
            return
        file.convert_status = (
            "error"
            if output and output.find("Conversion failed") != -1
            else "converted"
        )
        file.last_convert_msg = repr(output).replace("\\n", "\n").strip("'")
        file.converted_at = datetime.datetime.now(tz=timezone("UTC"))
        file.save()
