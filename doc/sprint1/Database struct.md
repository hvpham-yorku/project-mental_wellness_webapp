# Database Structure Documentation for MindSage

## 1. Users Table (Handled by Supabase)
Authentication for users, including registration, login, and session management, is handled by Supabase's built-in authentication system. The relevant tables (e.g., `auth.users`) are automatically managed by Supabase.

- **Users Table:** Managed by Supabase (contains information like `id`, `email`, `password_hash`, etc.).
- **Authentication Tokens:** Supabase handles session tokens for login, access, and refresh tokens automatically.




## 2. Journal Entries Table
The `journal_entries` table stores user-generated journal entries, allowing users to document their thoughts or experiences.

| Field         | Type      | Description                                        | Constraints                        |
|---------------|-----------|----------------------------------------------------|------------------------------------|
| id            | UUID      | Unique identifier for each journal entry          | Primary Key, Not Null              |
| user_id       | UUID      | Foreign key linking to the users table            | Foreign Key, Not Null, References `auth.users(id)` |
| content       | TEXT      | Content of the journal entry                       | Not Null                           |
| created_at    | TIMESTAMP | Timestamp of when the entry was created            | Not Null                           |
| updated_at    | TIMESTAMP | Timestamp of the last update to the entry          |                                    |

### Relationships:
- Many-to-one with users (`user_id` references `auth.users(id)`).

---

## 3. Mood Entries Table
The `mood_entries` table stores user mood tracking data, allowing users to record their emotional states and activities.

| Field         | Type      | Description                                        | Constraints                        |
|---------------|-----------|----------------------------------------------------|------------------------------------|
| id            | UUID      | Unique identifier for each mood entry             | Primary Key, Not Null              |
| user_id       | UUID      | Foreign key linking to the users table            | Foreign Key, Not Null, References `auth.users(id)` |
| happiness     | INT       | Numeric rating of happiness (1-10)                 | Not Null                           |
| anxiety       | INT       | Numeric rating of anxiety (1-10)                   | Not Null                           |
| energy        | INT       | Numeric rating of energy (1-10)                    | Not Null                           |
| stress        | INT       | Numeric rating of stress (1-10)                    | Not Null                           |
| activity      | VARCHAR(255) | Activity associated with the mood (e.g., exercise, work) | Not Null                           |
| notes         | TEXT      | Optional notes about the mood entry               |                                    |
| created_at    | TIMESTAMP | Timestamp of when the mood entry was created       | Not Null                           |

### Relationships:
- Many-to-one with users (`user_id` references `auth.users(id)`).

---

With this structure, we handle the authentication of users and store the content specific to each user’s activities and moods.
