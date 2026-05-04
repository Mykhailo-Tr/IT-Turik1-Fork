# API Leaderboard

---

## 1. Ендпоінти

| Дія | Метод | Шлях | Доступ |
| :--- | :--- | :--- | :--- |
| **Лідерборд раунду** | GET | `/api/evaluation/tournaments/rounds/{round_id}/leaderboard/` | Auth |
| **Лідерборд турніру (останній раунд)** | GET | `/api/evaluation/tournaments/{tournament_id}/leaderboard/` | Auth |

---

## 2. Режими

- `is_snapshot = true`
  - коли `tournament.status == finished`
  - дані читаються з `LeaderboardEntry` (архівний snapshot)
- `is_snapshot = false`
  - коли `round.status == evaluated` і турнір ще не `finished`
  - дані обчислюються live з `SubmissionEvaluation`

---

## 3. Доступ і видимість

- Обидва ендпоінти вимагають авторизацію (`IsAuthenticated`).
- Якщо раунд ще не `evaluated`:
  - роль `team` отримує `403 Forbidden`
  - ролі `admin`, `organizer`, `jury` можуть бачити live leaderboard
- Поле `jury_breakdown`:
  - завжди `null` для ролі `team`
  - видиме для `admin` / `organizer` / `jury`

---

## 4. GET `/api/evaluation/tournaments/rounds/{round_id}/leaderboard/`

### Успіх (`200`)

```json
{
  "round_id": 1,
  "is_snapshot": true,
  "rankings": [
    {
      "rank": 1,
      "team_id": 3,
      "team_name": "Team Alpha",
      "total_score": 87.5,
      "average_score": 29.2,
      "criteria_breakdown": {
        "Innovation": 30,
        "Design": 28,
        "Presentation": 29.5
      },
      "jury_breakdown": null
    }
  ]
}
```

### Помилки

- `404 Not Found` — раунд не існує
- `403 Forbidden` — роль `team`, а раунд ще не `evaluated`

---

## 5. GET `/api/evaluation/tournaments/{tournament_id}/leaderboard/`

Повертає лідерборд для **останнього раунду** турніру (сортування за `start_date`, `id`).

### Успіх (`200`)

Структура відповіді така сама:

```json
{
  "round_id": 5,
  "is_snapshot": false,
  "rankings": [
    {
      "rank": 1,
      "team_id": 8,
      "team_name": "Team Sigma",
      "total_score": 91.0,
      "average_score": 30.33,
      "criteria_breakdown": {
        "Innovation": 31,
        "Design": 30,
        "Presentation": 30
      },
      "jury_breakdown": {
        "jury1": 30.5,
        "jury2": 30.0
      }
    }
  ]
}
```

### Помилки

- `404 Not Found` — турнір не існує
- `404 Not Found` — у турніру немає раундів
- `403 Forbidden` — роль `team`, а останній раунд ще не `evaluated`

---

## 6. Життєвий цикл snapshot

- Snapshot створюється автоматично, коли турнір переходить у `finished`.
- Сервіс: `save_leaderboard_snapshot(tournament_id, round_id)`.
- Функція idempotent: повторний виклик не створює дублікати.
