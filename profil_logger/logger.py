import datetime

import re
from typing import List, Optional, Dict, Any
from collections import defaultdict

LOG_LEVEL_VALUES = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
DEFAULT_LOG_LEVEL = "DEBUG"


class LogEntry:
    def __init__(self, date: datetime.datetime, level: str, message: str):
        self.date = date
        self.level = level
        self.message = message

    def __repr__(self):
        return f"LogEntry(date={self.date.isoformat()}, level='{self.level}', message='{self.message}')"

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "level": self.level,
            "message": self.message,
        }

    @staticmethod
    def create_log_entry(data: Dict[str, str]) -> "LogEntry":
        return LogEntry(
            date=datetime.datetime.fromisoformat(data["date"]),
            level=data["level"],
            message=data["message"],
        )


class ProfileLogger:
    def __init__(self, handlers: List[Any]):
        self.handlers = handlers
        self.current_log_level_val = LOG_LEVEL_VALUES[DEFAULT_LOG_LEVEL]

    def _log(self, level: str, message: str) -> None:
        if LOG_LEVEL_VALUES[level] < self.current_log_level_val:
            return
        entry = LogEntry(date=datetime.datetime.now(), level=level, message=message)
        for handler_item in self.handlers:
            self.write_to_handler(handler_item, entry)

    def write_to_handler(self, handler: Any, entry: LogEntry) -> None:
        persist_methods = [
            "persist_log_sql",
            "persist_log_json",
            "persist_log_csv",
            "persist_log_file",
        ]
        last_exception = None
        for method_name in persist_methods:
            if hasattr(handler, method_name):
                try:
                    method = getattr(handler, method_name)
                    method(entry)
                    return
                except Exception as e:
                    last_exception = e
                    continue

        error_msg = (
            f"ERROR: All handlers failed. Final error on {type(handler).__name__}"
        )

        if last_exception:
            error_msg += f". Last error {last_exception}"
        print(error_msg)

    def info(self, message: str) -> None:
        self._log("INFO", message)

    def warning(self, message: str) -> None:
        self._log("WARNING", message)

    def critical(self, message: str) -> None:
        self._log("CRITICAL", message)

    def error(self, message: str) -> None:
        self._log("ERROR", message)

    def debug(self, message: str) -> None:
        self._log("DEBUG", message)

    def set_log_level(self, level: str) -> None:
        self.current_log_level_val = LOG_LEVEL_VALUES.get(
            level.upper(), self.current_log_level_val
        )


class ProfileLoggerReader:
    def __init__(self, handler: Any):
        self.handler = handler

    def get_all_logs_from_handler(self) -> List[LogEntry]:
        retrieval_methods = [
            "retrieve_all_logs_sql",
            "retrieve_all_logs_json",
            "retrieve_all_logs_csv",
            "retrieve_all_logs_file",
        ]

        for method_name in retrieval_methods:
            if hasattr(self.handler, method_name):
                try:
                    method = getattr(self.handler, method_name)
                    return method()
                except Exception as e:
                    print(f"{method_name}: {e}")
                    continue
        print(
            f"ERROR: Handler {type(self.handler).__name__} has no recognized retrieval method."
        )
        return []

    @staticmethod
    def filter_by_date(
        logs: List[LogEntry],
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
    ) -> List[LogEntry]:
        if not start_date and not end_date:
            return logs
        filtered_logs = []
        for log in logs:
            if start_date < log.date <= end_date:
                filtered_logs.append(log)
        return filtered_logs

    def find_by_text(self, text: str, start_date=None, end_date=None) -> List[LogEntry]:
        all_logs = self.get_all_logs_from_handler()
        filter_by_time = self.filter_by_date(all_logs, start_date, end_date)
        result_logs = [log for log in filter_by_time if text in log.message]
        return result_logs

    def find_by_regex(
        self, regex: str, start_date=None, end_date=None
    ) -> List[LogEntry]:
        pattern = re.compile(regex.lower())
        all_logs = self.get_all_logs_from_handler()
        filtered_by_date = self.filter_by_date(all_logs, start_date, end_date)
        try:
            matching_logs = [
                log for log in filtered_by_date if pattern.search(log.message.lower())
            ]
            return matching_logs
        except re.error as e:
            print(f"No logs with '{regex}' pattern ")
            return []

    def group_by_level(
        self, start_date=None, end_date=None
    ) -> Dict[str, List[LogEntry]]:
        all_logs = self.get_all_logs_from_handler()
        filter_logs = self.filter_by_date(all_logs, start_date, end_date)

        grouped = defaultdict(list)
        for log_entry in filter_logs:
            level = log_entry.level
            grouped[level].append(log_entry)

        return grouped

    def group_by_month(
        self, start_date=None, end_date=None
    ) -> Dict[str, List[LogEntry]]:
        all_logs = self.get_all_logs_from_handler()
        logs_to_group = self.filter_by_date(all_logs, start_date, end_date)
        grouped_by_month = defaultdict(list)
        for log_entry in logs_to_group:
            key = log_entry.date.strftime("%Y-%m")
            grouped_by_month[key].append(log_entry)
        return grouped_by_month
