# EcoCollect entity relationship diagram

```mermaid
erDiagram
    users ||--o{ collection_requests : submits
    users ||--o{ status_history : changes
    recycling_centres o|--o{ collection_requests : assigned_to
    collection_requests ||--|{ request_items : contains
    ewaste_categories ||--o{ request_items : classifies
    collection_requests ||--|{ status_history : records
    users {
      int id PK
      varchar name
      varchar email UK
      varchar password_hash
      varchar role
      datetime created_at
    }
    ewaste_categories {
      int id PK
      varchar name UK
    }
    recycling_centres {
      int id PK
      varchar name UK
      varchar address
      varchar phone
      boolean active
    }
    collection_requests {
      int id PK
      int user_id FK
      int centre_id FK "Nullable until scheduled"
      varchar address
      varchar status
      date pickup_date
      datetime created_at
    }
    request_items {
      int id PK
      int request_id FK
      int category_id FK
      varchar condition
      int quantity
      decimal estimated_weight
      decimal actual_weight "Nullable until collected"
    }
    status_history {
      int id PK
      int request_id FK
      int changed_by FK
      varchar status
      datetime changed_at
      varchar note
    }
```

The API enforces at least one item and an initial history event per request. Foreign keys enforce that child rows have a valid parent. Item weights describe the entire row, not one unit. All timestamps are UTC; pickup dates are local calendar dates.
