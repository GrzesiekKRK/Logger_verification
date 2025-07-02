import datetime
import pytest
import os
import tempfile
import json

from .logger import LogEntry, ProfileLogger, ProfileLoggerReader
from .handlers import FileHandler, JsonHandler, SQLiteHandler, CSVHandler


class TestLogEntry:
    def setup_method(self):
        self.log_entry = LogEntry(
            date=datetime.datetime(2022, 11, 1, 12, 0, 0), level="INFO", message="test"
        )

    def test_log_entry_constructor(self):
        expected_date = datetime.datetime(2022, 11, 1, 12, 0, 0)

        assert self.log_entry.date == expected_date
        assert self.log_entry.level == "INFO"
        assert self.log_entry.message == "test"
        assert isinstance(self.log_entry, LogEntry)

    def test_repr(self):
        expected_value = f"LogEntry(date={self.log_entry.date.isoformat()}, level='{self.log_entry.level}', message='{self.log_entry.message}')"
        assert repr(self.log_entry) == expected_value

    def test_to_dict(self):
        result_dict = self.log_entry.to_dict()

        assert result_dict["date"] == self.log_entry.date.isoformat()
        assert result_dict["level"] == self.log_entry.level
        assert result_dict["message"] == self.log_entry.message
        assert len(result_dict) == 3

    def test_create_log_entry(self):
        data = {
            "date": "2022-11-01T12:00:00",  # ISO format string
            "level": "INFO",
            "message": "test_create_log_entry",
        }

        test_instance = LogEntry.create_log_entry(data)

        assert isinstance(test_instance, LogEntry)
        assert test_instance.date == datetime.datetime(2022, 11, 1, 12, 0, 0)
        assert test_instance.level == data["level"]
        assert test_instance.message == data["message"]

    def test_create_log_entry_with_invalid_date(self):
        data = {"date": "invalid-date", "level": "INFO", "message": "test"}

        with pytest.raises(ValueError):
            LogEntry.create_log_entry(data)

    def test_create_log_entry_missing_keys(self):
        data = {"level": "INFO", "message": "test"}

        with pytest.raises(KeyError):
            LogEntry.create_log_entry(data)


class TestProfileLogger:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.json_file = os.path.join(self.temp_dir, "test.json")
        self.csv_file = os.path.join(self.temp_dir, "test.csv")
        self.log_file = os.path.join(self.temp_dir, "test.log")
        self.db_file = os.path.join(self.temp_dir, "test.db")

        self.json_handler = JsonHandler(self.json_file)
        self.csv_handler = CSVHandler(self.csv_file)
        self.file_handler = FileHandler(self.log_file)
        self.sqlite_handler = SQLiteHandler(self.db_file)

        self.logger = ProfileLogger(
            [
                self.json_handler,
                self.csv_handler,
                self.file_handler,
                self.sqlite_handler,
            ]
        )
        self.logger.debug("Debug")
        self.logger.info("Logging started")
        self.logger.warning("Warning occurred")
        self.logger.error("Error occurred")
        self.logger.critical("Critical occurred")

    def test_logger_creation(self):
        assert isinstance(self.logger, ProfileLogger)
        assert len(self.logger.handlers) == 4

    def test_log_levels(self):
        self.logger.debug("debug message")
        self.logger.info("info message")
        self.logger.warning("warning message")
        self.logger.error("error message")
        self.logger.critical("critical message")

        reader = ProfileLoggerReader(self.json_handler)
        logs = reader.get_all_logs_from_handler()

        assert len(logs) == 10 #5 setup add 5 added in this test
        assert logs[0].level == "DEBUG"
        assert logs[1].level == "INFO"
        assert logs[2].level == "WARNING"
        assert logs[3].level == "ERROR"
        assert logs[4].level == "CRITICAL"

    def test_set_log_level(self):
        self.logger.set_log_level("WARNING")
        self.logger.info("too low")
        self.logger.info("too low")
        self.logger.debug("too low")
        reader = ProfileLoggerReader(self.json_handler)
        only_set_up_logs = reader.get_all_logs_from_handler()
        self.logger.warning("works")
        additional_warning_log = reader.get_all_logs_from_handler()
        warning_error = []
        for log in only_set_up_logs:
            if log.level == "WARNING" or log.level == "ERROR":
                warning_error.append(log)
        assert len(only_set_up_logs) == 5
        assert len(warning_error) == 2
        assert len(additional_warning_log) == 6

    def test_invalid_log_level(self):
        original_level = self.logger.current_log_level_val
        self.logger.set_log_level("INVALID")

        assert self.logger.current_log_level_val == original_level


class TestProfileLoggerReader:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.json_file = os.path.join(self.temp_dir, "test.json")
        self.handler = JsonHandler(self.json_file)
        self.reader = ProfileLoggerReader(self.handler)

        test_logs = [
            LogEntry(datetime.datetime(2022, 1, 1, 10, 0), "DEBUG", "debug msg"),
            LogEntry(datetime.datetime(2022, 1, 2, 11, 0), "INFO", "info msg"),
            LogEntry(datetime.datetime(2022, 2, 1, 12, 0), "WARNING", "warning msg"),
            LogEntry(datetime.datetime(2022, 2, 2, 13, 0), "ERROR", "error msg"),
        ]

        for log in test_logs:
            self.handler.persist_log_json(log)

    def teardown_method(self):
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_all_logs(self):
        logs = self.reader.get_all_logs_from_handler()
        assert len(logs) == 4

    def test_filter_by_date(self):
        start_date = datetime.datetime(2022, 1, 1)
        end_date = datetime.datetime(2022, 1, 31)

        all_logs = self.reader.get_all_logs_from_handler()
        filtered = self.reader.filter_by_date(all_logs, start_date, end_date)

        assert len(filtered) == 2

    def test_find_by_text(self):
        results = self.reader.find_by_text("info")
        assert len(results) == 1
        assert results[0].message == "info msg"

    def test_find_by_regex(self):
        results = self.reader.find_by_regex(r"(debug|info)")
        assert len(results) == 2

    def test_group_by_level(self):
        grouped = self.reader.group_by_level()

        assert len(grouped["DEBUG"]) == 1
        assert len(grouped["INFO"]) == 1
        assert len(grouped["WARNING"]) == 1
        assert len(grouped["ERROR"]) == 1
        assert len(grouped["CRITICAL"]) == 0

    def test_group_by_month(self):
        grouped = self.reader.group_by_month()

        assert len(grouped["01"]) == 0
        assert len(grouped["02"]) == 0
        assert len(grouped["03"]) == 0


class TestHandlers:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_json_handler_roundtrip(self):
        json_file = os.path.join(self.temp_dir, "test.json")
        handler = JsonHandler(json_file)

        log_entry = LogEntry(
            datetime.datetime(2022, 1, 1, 12, 0), "INFO", "test message"
        )
        handler.persist_log_json(log_entry)

        logs = handler.retrieve_all_logs_json()

        assert len(logs) == 1
        assert logs[0].level == "INFO"
        assert logs[0].message == "test message"

    def test_csv_handler_roundtrip(self):
        csv_file = os.path.join(self.temp_dir, "test.csv")
        handler = CSVHandler(csv_file)

        log_entry = LogEntry(
            datetime.datetime(2022, 1, 1, 12, 0), "INFO", "test message"
        )

        handler.persist_log_csv(log_entry)
        logs = handler.retrieve_all_logs_csv()

        assert len(logs) == 1
        assert logs[0].level == "INFO"

    def test_file_handler_special_characters(self):
        log_file = os.path.join(self.temp_dir, "test.log")
        handler = FileHandler(log_file)

        log_entry = LogEntry(
            datetime.datetime(2022, 1, 1, 12, 0),
            "INFO",
            "message with spaces and special chars: !@#$%",
        )

        handler.persist_log_file(log_entry)
        logs = handler.retrieve_all_logs_file()

        assert len(logs) == 1
        assert logs[0].message == "message with spaces and special chars: !@#$%"
