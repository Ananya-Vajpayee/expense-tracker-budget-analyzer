# Design Documentation

Diagrams are written in Mermaid (renders on GitHub). Export them as images for the PDF report via https://mermaid.live.

## Functional Requirements
| ID | Requirement |
|----|-------------|
| FR1 | Add an expense (amount, category, description, date) |
| FR2 | List/filter expenses by month and category |
| FR3 | Edit and delete expenses |
| FR4 | Set, view and remove category budgets |
| FR5 | Warn when a budget reaches 80% or is exceeded |
| FR6 | Generate monthly summary with category chart and projection |
| FR7 | Export expenses to CSV |

## Non-Functional Requirements
| Type | Requirement |
|------|-------------|
| Usability | Clear CLI messages; interactive menu and subcommands |
| Reliability | Atomic writes; corrupt data file backed up, app keeps running |
| Security/Validation | All input validated (positive amounts, valid dates/months, bounded category length) |
| Maintainability | Modular design, one responsibility per file, unit tests |
| Performance | Operations on thousands of records complete in milliseconds |
| Logging | Events and errors written to `logs/app.log` |

## System Architecture
```mermaid
flowchart TB
    U[User / Terminal] --> M[main.py]
    M --> C[cli.py]
    C --> EM[ExpenseManager]
    C --> BM[BudgetManager]
    C --> R[report.py]
    EM --> V[validators.py]
    BM --> V
    BM --> A[analytics.py]
    R --> A
    EM --> S[(DataStore - JSON file)]
    BM --> S
    C -.-> L[logger_config.py]
```

## Use Case Diagram
```mermaid
flowchart LR
    User((User))
    User --- UC1[Add expense]
    User --- UC2[View / filter expenses]
    User --- UC3[Edit / delete expense]
    User --- UC4[Set budget]
    User --- UC5[Check budget status]
    User --- UC6[View monthly summary]
    User --- UC7[Export CSV]
    UC1 -. includes .-> UC8[Validate input]
    UC1 -. extends .-> UC9[Budget warning]
```

## Workflow Diagram
```mermaid
flowchart TD
    A[Start] --> B{Command given?}
    B -- No --> C[Show menu]
    B -- Yes --> D[Parse arguments]
    C --> D
    D --> E[Validate input]
    E -- Invalid --> F[Show error, log warning]
    E -- Valid --> G[Execute action on DataStore]
    G --> H[Save JSON atomically]
    H --> I[Print result / budget warning]
    F --> J[End or return to menu]
    I --> J
```

## Sequence Diagram (Add Expense)
```mermaid
sequenceDiagram
    actor User
    participant CLI as cli.py
    participant EM as ExpenseManager
    participant V as validators
    participant DS as DataStore
    participant BM as BudgetManager
    User->>CLI: add --amount 250 --category food
    CLI->>EM: add(...)
    EM->>V: validate amount/category/date
    V-->>EM: cleaned values
    EM->>DS: append + save()
    DS-->>EM: ok
    EM-->>CLI: Expense
    CLI->>BM: status(month)
    BM-->>CLI: budget rows
    CLI-->>User: confirmation + warning if any
```

## Class Diagram
```mermaid
classDiagram
    class Expense {
        +int id
        +float amount
        +str category
        +str description
        +str date
        +to_dict()
        +from_dict()
    }
    class DataStore {
        +list expenses
        +dict budgets
        +load()
        +save()
        +next_id()
    }
    class ExpenseManager {
        +add()
        +get()
        +list()
        +update()
        +delete()
    }
    class BudgetManager {
        +set_budget()
        +remove_budget()
        +status()
    }
    ExpenseManager --> DataStore
    BudgetManager --> DataStore
    DataStore "1" o-- "*" Expense
```

## Storage Design (ER)
```mermaid
erDiagram
    EXPENSE {
        int id PK
        float amount
        string category FK
        string description
        date date
    }
    BUDGET {
        string category PK
        float limit
    }
    BUDGET ||--o{ EXPENSE : "limits spending on"
```
Stored as one JSON document: `{"expenses": [...], "budgets": {...}}`.

## Design Decisions & Rationale
- **JSON over a database**: zero setup, human-readable, enough for personal data.
- **Single shared `DataStore`**: managers can't overwrite each other's changes.
- **Pure functions in `analytics.py`**: easy to test, no side effects.
- **Atomic save (temp file + replace)**: prevents data loss on crash.
- **argparse + menu**: scriptable for the evaluator, friendly for humans.
