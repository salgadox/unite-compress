import logging

from celery import shared_task
from django.db import connections

from unite_compress.files.models import (
    CONVERSION_STATUS_CHOICES,
    ConvertingCommand,
    File,
)
from unite_compress.files.utils import Converter

logger = logging.getLogger(__name__)


@shared_task(time_limit=7200)
def convert_file(command_id, file_id):
    command = ConvertingCommand.objects.get(pk=command_id)
    file = File.objects.get(pk=file_id)
    started = CONVERSION_STATUS_CHOICES[1][0]
    if File.convert_status in [started]:
        logger.error(f"File #{file_id} is already converted")
        return
    converter = Converter()
    converter.convert_file(command, file)
    connections.close_all()  # dubious step for fix Celery beat problem
