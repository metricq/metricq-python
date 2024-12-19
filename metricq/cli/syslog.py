import logging
import socket
import time
from logging.handlers import SysLogHandler


class SyslogFormatter(logging.Formatter):
    def __init__(self, *args, name: str = "metricq", **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)
        self.program = name

    def format(self, record: logging.LogRecord) -> str:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        hostname = socket.gethostname()
        pid = record.process
        program = self.program
        # Custom Formatter based on rfc3164
        # Format the header as "<PRI> TIMESTAMP HOSTNAME PROGRAM[PID]: MESSAGE"
        # <PRI> is already being set by the SysLogHandler, we only need to add the rest
        syslog_header = f"{timestamp} {hostname} {program}[{pid}]: "
        message = super().format(record)
        return syslog_header + message


def get_syslog_handler(address: str | None) -> SysLogHandler:
    if address is None:
        return SysLogHandler()
    elif ":" in address:
        ip, port = address.split(":")
        return SysLogHandler(address=(ip, int(port)))
    else:
        return SysLogHandler(address=address)
