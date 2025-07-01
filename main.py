import datetime

from icecream import ic

# test_reading.py
from profil_logger.logger import ProfileLogger, ProfileLoggerReader
from profil_logger.handlers import JsonHandler, CSVHandler, SQLiteHandler, FileHandler


def log_json(handler):
    reader = ProfileLoggerReader(handler)
    logs = reader.get_all_logs_from_handler()
    ic(f"Found {len(logs)} json logs:")
    # find_by_text = reader.find_by_regex('First',
    #                                              start_date=datetime.datetime(2025, 7, 1, hour=16, minute=30),
    #                                              end_date=datetime.datetime(2025, 7, 1, hour=16, minute=41)
    #                                              )
    # ic("filtrowanie json", find_by_text)
    find_by_text = reader.find_by_regex(
        "mess", end_date=datetime.datetime(2025, 7, 1, hour=16, minute=41)
    )
    ic("filtrowanie json", find_by_text)


def log_csv(handler):
    reader_csv = ProfileLoggerReader(handler)
    logs_csv = reader_csv.get_all_logs_from_handler()
    ic(f"Found {len(logs_csv)} csv logs:")


def log_sql(handler):
    reader_sql = ProfileLoggerReader(handler)
    logs_sql = reader_sql.get_all_logs_from_handler()
    ic(f"Found {len(logs_sql)} sql logs:")


def log_file_handler(handler):
    reader = ProfileLoggerReader(handler)
    logs_file_handler = reader.get_all_logs_from_handler()
    ic(f"Found {len(logs_file_handler)} log entries:")


def start():
    handler_json = JsonHandler("logs.json")
    handler_csv = CSVHandler("logs.csv")
    handler_sql = SQLiteHandler("logs.sql")
    handler_file = FileHandler("logs.txt")
    logger = ProfileLogger([handler_json, handler_csv, handler_sql, handler_file])
    # logger.info("First message")
    # logger.warning("Second message")
    # logger.error("Third message")
    log_json(handler_json)
    log_csv(handler_csv)
    log_sql(handler_sql)
    log_file_handler(handler_file)


if __name__ == "__main__":
    start()
