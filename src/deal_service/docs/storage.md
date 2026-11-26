
# Deal Service — Storage Design

## 1. Database

The service uses SQLite as its database and SQLAlchemy as ORM.

### Tables

#### deals

Stores general deal information.

| Column | Type | Description |
|---|---|---|
| id | TEXT PK | Unique deal identifier |
| status | TEXT | Current deal status |
| created_at | DATETIME | Creation timestamp |

#### deal_fields

Stores vehicle and seller information.

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Field identifier |
| deal_id | TEXT FK | Related deal |
| name | TEXT | Field name |
| value | TEXT NULL | Field value |
| status | TEXT | Field verification status |

Unique constraint: (deal_id, name).

#### participants

Stores users participating in a deal.

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Participant identifier |
| deal_id | TEXT FK | Related deal |
| user_id | TEXT | User identifier |
| role | TEXT | client or manager |

Unique constraint: (deal_id, user_id).

#### messages

Stores chat messages.

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Message identifier |
| deal_id | TEXT FK | Related deal |
| sender_id | TEXT | Sender identifier |
| text | TEXT NULL | Message content |
| created_at | DATETIME | Creation timestamp |

#### attachments

Stores attachment metadata. Actual files are stored on disk.

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Attachment identifier |
| message_id | INTEGER FK | Related message |
| filename | TEXT | Original filename |
| storage_path | TEXT | File storage path |
| content_type | TEXT | MIME type |

A message can contain multiple attachments.

## 2. Relationships

- One deal has multiple fields.
- One deal has multiple participants.
- One deal has multiple messages.
- One message can have multiple attachments.

## 3. Field statuses

| Status | Description |
|---|---|
| pending | Awaiting manager review |
| approved | Approved by manager |
| changes_requested | Client must correct the value |

### Allowed transitions

- pending -> approved
- pending -> changes_requested
- changes_requested -> pending (after client modification)
- approved -> terminal state (editing prohibited)

## 4. Deal statuses

| Status | Description |
|---|---|
| in_progress | Deal is being processed |
| completed | Client completed the buyout |
| received | Vehicle accepted into warehouse |

### Allowed transitions

**in_progress -> completed**

Triggered by the client through POST /deals/{dealId}/complete.

Conditions:
- All required fields have values.
- All required fields are approved.

**completed -> received**

Triggered by the manager through POST /deals/{dealId}/receive.

Condition:
- Deal status must be completed.

No other status transitions are allowed.

## 5. Demo data

Deal ID: deal-001

Participants:
- client-001 (client)
- manager-001 (manager)

The demo deal contains 10 vehicle and seller fields.

Initial deal status: in_progress.

Initial field status: pending.
