#  API Cheat Sheet


---

### 1. Турніри

| Дія | Метод | Шлях | Доступ |
| :--- | :--- | :--- | :--- |
| **Список турнірів** | GET | `/api/tournaments/` | Всі |
| **Деталі турніру** | GET | `/api/tournaments/{id}/` | Всі |
| **Створити турнір** | POST | `/api/tournaments/manage/` | Admin |
| **Редагувати турнір** | PATCH/DEL| `/api/tournaments/manage/{id}/` | Admin |
| **Відкрити реєстрацію**| POST | `/api/tournaments/{id}/start-registration/` | Admin |
| **Реєстрація команди** | POST | `/api/tournaments/{id}/register-team/` | Капітан |
| **Список раундів** | GET | `/api/tournaments/rounds/` | Admin |
| **Створити раунд** | POST | `/api/tournaments/rounds/` | Admin |
| **Деталі/Зміна раунду**| GET/PATCH | `/api/tournaments/rounds/{id}/` | Admin |
| **Почати раунд** | POST | `/api/tournaments/rounds/{id}/start/` | Admin |
| **Закрити прийом робіт**| POST | `/api/tournaments/rounds/{id}/close-submissions/` | Admin |
| **Фіналізація оцінок** | POST | `/api/tournaments/rounds/{id}/mark-evaluated/` | Admin |
| **Мої роботи** | GET | `/api/tournaments/submissions/` | Команда |
| **Подати роботу** | POST | `/api/tournaments/submissions/` | Команда |
| **Деталі/Зміна роботи** | GET/PATCH | `/api/tournaments/submissions/{id}/` | Команда |
| **Поточне завдання** | GET | `/api/tournaments/current-task/` | Учасники |

### 2. Раунди 

| Дія | Метод | Шлях | Доступ |
| :--- | :--- | :--- | :--- |
| **Розподіл робіт (журі)**| POST | `/api/evaluation/rounds/{id}/assign-jury/` | Admin |
| **Призначені роботи** | GET | `/api/evaluation/assignments/` | Jury |
| **Відправити оцінку** | POST | `/api/evaluation/evaluate/` | Jury |
| **Перегл/Зміна/Вид. оцінки**| GET/PATCH/DEL| `/api/evaluation/evaluate/{id}/` | Jury |



---

### 1. Турніри (Admin)

**Створення турніру — POST `/api/tournaments/manage/`**
```json
{
  "name": "Hack 2026",
  "description": "Build a scalable backend",
  "start_date": "2026-05-01T10:00:00Z",
  "end_date": "2026-05-10T10:00:00Z",
  "rounds_count": 2,
  "max_teams": 20,
  "min_team_members": 2,
  "criteria": [
    {
      "id": "backend",
      "name": "Backend Quality",
      "description": "Code quality",
      "max_score": 10
    }
  ]
}
```

**Редагування турніру — PATCH `/api/tournaments/manage/{id}/`**
```json
{
  "max_teams": 25,
  "description": "Updated hackathon description"
}
```

**Реєстрація команди — POST `/api/tournaments/{id}/register-team/`**
```json
{ "team_id": 10 }
```

### 2. Раунди (Admin)

**Створення раунду — POST `/api/tournaments/rounds/`**
```json
{
  "tournament": 1,
  "position": 2,
  "name": "Final Stage",
  "start_date": "2026-05-05T10:00:00Z",
  "end_date": "2026-05-07T18:00:00Z",
  "passing_count": 5,
  "tech_requirements": {},
  "must_have_requirements": {},
  "description": "Round description text"
}
```

**Редагування раунду — PATCH `/api/tournaments/rounds/{id}/`**
```json
{
  "passing_count": 8,
  "tech_requirements": {
    "db": "PostgreSQL"
  },
  "description": "Updated description"
}
```

### 3. Роботи (Команда)

**Подача роботи — POST `/api/tournaments/submissions/`**
```json
{
  "team": 1,
  "round": 1,
  "github_url": "https://github.com/user/repo",
  "demo_video_url": "https://youtube.com/...",
  "description": "Ready for review"
}
```

**Редагування роботи — PATCH `/api/tournaments/submissions/{id}/`**
```json
{
  "github_url": "https://github.com/user/new-repo-link",
  "description": "Updated submission notes"
}
```

### 4. Оцінювання (Jury/Admin)

**Розподіл робіт (Admin) — POST `/api/evaluation/rounds/{id}/assign-jury/`**
```json
{ "k": 2 } 
```

**Створення оцінки (Jury) — POST `/api/evaluation/evaluate/`**
```json
{
  "assignment": 1,
  "scores": [
    { "criterion_id": "backend", "score": 10 },
    { "criterion_id": "db", "score": 8 }
  ],
  "comment": "Excellent work!"
}
```
*Response Example:*
```json
{
  "id": 12,
  "assignment": 1,
  "scores": [
    { "criterion_id": "backend", "score": 10 },
    { "criterion_id": "db", "score": 8 }
  ],
  "comment": "Excellent work!",
  "total_score": 18,
  "final_score": 9.0,
  "created_at": "2026-04-26T10:00:00Z"
}
```

**Оновлення оцінки (Jury) — PATCH `/api/evaluation/evaluate/{id}/`**
```json
{
  "scores": [
    { "criterion_id": "backend", "score": 9 },
    { "criterion_id": "db", "score": 8 }
  ],
  "comment": "Revised score after check"
}
```

> **Важливо для оцінювання:**
> - Кожен `criterion_id` має точно збігатися з id критерію з турніру.
> - Оцінка `score` має бути $\ge 0$ та $\le$ `max_score` критерію.
> - Дублікати `criterion_id` не допускаються.
> - Необхідно передати оцінки для **всіх** критеріїв турніру. Якщо потрібен 0, його потрібно передати явно (`"score": 0`).
