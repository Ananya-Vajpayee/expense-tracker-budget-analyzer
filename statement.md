# Problem Statement

## Problem
Many students and young professionals do not track where their money goes. Spreadsheets are tedious, and most apps need accounts, internet access, or a GUI. As a result, people overspend in certain categories and only notice at the end of the month.

## Scope
The project is a **command-line Expense Tracker & Budget Analyzer** built with core Python. It covers:
- Recording, viewing, editing and deleting expenses (CRUD)
- Setting monthly budgets per category and warning when they are nearly used or exceeded
- Analytics: category totals, largest expense, month-end projection, text bar charts
- CSV export of expenses

Out of scope: multi-user accounts, cloud sync, bank integration, GUI/web front-end.

## Target Users
- Students managing a monthly allowance
- Beginners who want a simple, offline, privacy-friendly tracker
- Anyone comfortable running a terminal command

## High-Level Features
1. **Expense Management** - add / list / edit / delete with filters by month and category
2. **Budget Management** - per-category limits with OK / WARNING (>=80%) / EXCEEDED status
3. **Analytics & Reporting** - monthly summary, projections, ASCII charts, CSV export
4. **Reliability** - input validation, atomic JSON saves, corrupt-file recovery, logging
