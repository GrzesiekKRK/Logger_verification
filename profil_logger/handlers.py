from icecream import ic

import json
import csv
import sqlite3
import os
import datetime
from typing import List
from .logger import LogEntry


class JsonHandler:
    def __init__(self, filepath: str):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as file:
                json.dump([], file)

    def persist_log_json(self, entry: LogEntry):
        if os.path.exists(self.filepath) and os.path.getsize(self.filepath) > 0:
            with open(
                self.filepath,
                "r",
            ) as file:
                all_logs_data = json.load(file)
        else:
            all_logs_data = []

        all_logs_data.append(entry.to_dict())
        with open(
            self.filepath,
            "w",
        ) as file_out:
            json.dump(all_logs_data, file_out, indent=4)

    def retrieve_all_logs_json(self) -> List[LogEntry]:
        log_entries_list = []
        try:
            with open(
                self.filepath,
                "r",
            ) as file:
                data_dicts_list = json.load(file)
                for entry_dict_item in data_dicts_list:
                    log_entries_list.append(LogEntry.create_log_entry(entry_dict_item))
        except (FileNotFoundError, json.JSONDecodeError):
            return []
        return log_entries_list


class CSVHandler:
    def __init__(self, filepath: str):
        self.filepath = filepath
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
            with open(
                self.filepath,
                "w",
                newline="",
            ) as file:
                writer = csv.writer(file)
                writer.writerow(["date", "level", "message"])

    def persist_log_csv(self, entry: LogEntry) -> None:
        with open(
            self.filepath,
            "a",
            newline="",
        ) as file:
            writer = csv.writer(file)
            log_data_dict = entry.to_dict()
            writer.writerow(
                [
                    log_data_dict["date"],
                    log_data_dict["level"],
                    log_data_dict["message"],
                ]
            )

    def retrieve_all_logs_csv(self) -> List[LogEntry]:
        log_entries_list = []
        try:
            with open(
                self.filepath,
                "r",
                newline="",
            ) as file:
                reader = csv.DictReader(file)
                for row_as_dict in reader:
                    log_entries_list.append(LogEntry.create_log_entry(row_as_dict))
        except FileNotFoundError:
            return []
        return log_entries_list


class FileHandler:
    def __init__(self, filepath: str):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            with open(
                self.filepath,
                "w",
            ) as file:
                file.write("")

    def persist_log_file(self, entry: LogEntry) -> None:
        log_line = f"{entry.date.isoformat()} {entry.level} {entry.message}\n"
        with open(
            self.filepath,
            "a",
        ) as file:
            file.write(log_line)

    def retrieve_all_logs_file(self) -> List[LogEntry]:
        log_entries_list = []
        try:
            with open(
                self.filepath,
                "r",
            ) as file:
                for line_content_str in file.readlines():
                    parts = line_content_str.strip().split(" ", 2)
                    if len(parts) == 3:
                        log_entries_list.append(
                            LogEntry(
                                date=datetime.datetime.fromisoformat(parts[0]),
                                level=parts[1],
                                message=parts[2],
                            )
                        )
        except (FileNotFoundError, ValueError):
            return []
        return log_entries_list


class SQLiteHandler:
    def __init__(self, db_path: str, table_name: str = "logs"):
        self.db_path = db_path
        self.table_name = table_name
        self.create_table_if_not_exists()

    def get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def create_table_if_not_exists(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL
                )
            """
            cursor.execute(create_table_sql)
            conn.commit()

    def persist_log_sql(self, entry: LogEntry):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            sql_query = f"INSERT INTO {self.table_name} (timestamp, level, message) VALUES ('{entry.date.isoformat()}', '{entry.level}', '{entry.message}')"
            cursor.executescript(sql_query)
            conn.commit()

    def retrieve_all_logs_sql(self) -> List[LogEntry]:
        log_entries_list = []
        try:
            with self.get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"SELECT timestamp, level, message FROM {self.table_name} ORDER BY timestamp ASC"
                )
                for row in cursor.fetchall():
                    log_entries_list.append(
                        LogEntry(
                            date=datetime.datetime.fromisoformat(row[0]),
                            level=row[1],
                            message=row[2],
                        )
                    )
        except (sqlite3.Error, ValueError):
            return []
        return log_entries_list
