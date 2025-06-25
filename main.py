import datetime

from icecream import ic

# test_reading.py
from profil_logger.logger import ProfileLogger, ProfileLoggerReader
from profil_logger.handlers import JsonHandler, CSVHandler, SQLiteHandler, FileHandler


def log_json(handler):
    reader = ProfileLoggerReader(handler)
    logs = reader.get_all_logs_from_handler()
    ic(f"Found {len(logs)} json logs:")

    # Test search
    warning_logs = reader.find_by_text("warning")
    ic(f"Found {len(warning_logs)} warnings")

    # Test grouping
    grouped_level = reader.group_by_level()
    ic(f"Levels: {list(grouped_level.keys())}")
    grouped_month = reader.group_by_month()
    ic(f"Months: {list(grouped_month.keys())}")

    find_by_regex = reader.find_by_regex("INFO")
    ic(f"Found {len(find_by_regex)} info entries")
    find_by_text = reader.find_by_text("INFO")
    ic(f"Found {len(find_by_text)} info entries")


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
    filtered_by_hour = reader.filter_by_date(logs_file_handler,
                                             start_date=datetime.datetime(2025, 6, 25, hour=18, minute=30),
                                             end_date=datetime.datetime(2025, 6, 25, hour=18, minute=58)
                                             )

    ic(f"Found {len(logs_file_handler)} log entries:")
    ic(filtered_by_hour)


def start():
    handler_json = JsonHandler("logs.json")
    handler_csv = CSVHandler("logs.csv")
    handler_sql = SQLiteHandler("logs.sql")
    handler_file = FileHandler("logs.txt")
    logger = ProfileLogger([handler_json, handler_csv, handler_sql, handler_file])
    logger.info("First message")
    logger.warning("Second message")
    logger.error("Third message")
    # log_json(handler_json)
    # log_csv(handler_csv)
    # log_sql(handler_sql)
    log_file_handler(handler_file)



if __name__ == "__main__":
    start()
