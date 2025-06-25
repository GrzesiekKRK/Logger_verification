***

### Python Internship Programming Challenge: Refactoring a Logging Library

**Welcome, Candidate!**

This task is designed to assess your understanding of Python best practices and software design principles. You will be working with a small, functional logging library that has accumulated significant technical debt.

---

#### Section 1: Project Overview

The project consists of a small but flexible logging library with the following components:

*   **`ProfilLogger`**: The main interface for logging messages at different levels (e.g., INFO, ERROR).
*   **Handlers (`JsonHandler`, `CSVHandler`, `FileHandler`, `SQLLiteHandler`)**: A set of classes responsible for persisting log entries to different storage backends (a JSON file, a CSV file, a plain text file, and an SQLite database).
*   **`ProfilLoggerReader`**: A class used to read, search, and group log entries from a given handler.
*   **`LogEntry`**: A simple data class representing a single log message.

While the library "works," it was written hastily. It contains numerous bugs, security vulnerabilities, performance issues, and code smells.

---

#### Section 2: The Challenge

Your task is to **refactor the provided Python code**. You should transform it from its current state into a clean, maintainable, robust, and professional-grade module.

The primary goal is **not to add new features**, but to improve the quality of the existing implementation while ensuring its core functionality remains intact (after fixing the bugs).

---

#### Section 3: Core Requirements

You must address the following points in your submission.

**1. Refactoring and Code Quality:**
Your main focus should be on identifying and fixing the problems in the code. This includes, but is not limited to:
* Identify and fix the critical vulnerabilities.
* Replace inefficient algorithms with more performant solutions.
* Find and fix logical bugs.
* Improve variable names, add type hints where they are unclear.
* Ensure resources like file handles and database connections are managed correctly.
* Eliminate functions with hidden side effects.

**2. Functionality Preservation:**
The refactored code must behave the same as the original from a user's perspective, once the obvious bugs are corrected. For example, `groupby_level` should still group logs by their level, but it should do so correctly and efficiently.

**3. Testing:**
You must write a comprehensive test suite using a standard framework like **`pytest`**

**4. Tools configuraiton:**
Make sure to inlcude all necessary configuration files for the tools you used (e.g. `pyproject.toml`)

---

### Rules & hints

* Use Python 3.12 or greater
* Use `ruff` for ensuring code quality
* Use OOP paradigm
* You are not allowed to use any third-party libraries
* Provide README with examples of how to use your library
* Please put your solution in a private repository on Github and invite reviewer@profil-software.com as collaborator (any role with at least read-only access to code) -> https://docs.github.com/en/github/setting-up-and-managing-your-github-user-account/inviting-collaborators-to-a-personal-repository