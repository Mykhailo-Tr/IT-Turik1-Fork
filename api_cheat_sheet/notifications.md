# Notifications API — Cheat Sheet

Full reference for the notification system: endpoints, event types, channels, settings, and frontend integration.

---

## Endpoints

### Notification Management

| Action | Method | URL | Auth |
| :--- | :--- | :--- | :--- |
| List notifications | `GET` | `/api/notifications/` | ✅ Required |
| Mark one as read | `POST` | `/api/notifications/{id}/read/` | ✅ Recipient |
| Mark all as read | `POST` | `/api/notifications/read-all/` | ✅ Required |
| Delete one | `DELETE` | `/api/notifications/{id}/delete/` | ✅ Recipient |
| Delete all | `DELETE` | `/api/notifications/delete-all/` | ✅ Required |
| Unread count | `GET` | `/api/notifications/unread-count/` | ✅ Required |

### Notification Settings

| Action | Method | URL | Auth |
| :--- | :--- | :--- | :--- |
| Get personal settings | `GET` | `/api/notifications/settings/` | ✅ Required |
| Update per-event config | `POST` | `/api/notifications/settings/config/update/` | ✅ Required |
| Toggle all emails | `POST` | `/api/notifications/settings/global/update/` | ✅ Required |

---

## Pagination

`GET /api/notifications/` supports query params:

| Param | Default | Max | Description |
| :--- | :--- | :--- | :--- |
| `page` | `1` | — | Page number |
| `page_size` | `10` | `100` | Items per page |

**Example:** `/api/notifications/?page=1&page_size=50`

**Response shape:**
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/notifications/?page=2",
  "previous": null,
  "results": [
    {
      "id": 12,
      "event_type": "team_invitation_received",
      "title": "Team Invitation",
      "message": "You have received an invitation to join team \"Alpha\" from john_doe.",
      "is_read": false,
      "created_at": "2026-05-05T20:00:00Z"
    }
  ]
}
```

> Notifications older than **30 days** are automatically deleted on each list request.

---

## Event Types

All events are defined in `notifications/config.py`.

### Team Invitations

| `event_type` | Channels | Recipient | Redirect |
| :--- | :--- | :--- | :--- |
| `team_invitation_received` | system + email | Invited user | `/teams` |
| `team_invitation_accepted` | system | Team captain | `/teams/<id>` |
| `team_invitation_declined` | system | Team captain | `/teams/<id>` |

### Join Requests

| `event_type` | Channels | Recipient | Redirect |
| :--- | :--- | :--- | :--- |
| `team_join_request_received` | system + email | Team captain | `/teams/<id>` |
| `team_join_request_accepted` | system | Requesting user | `/teams/<id>` |
| `team_join_request_declined` | system | Requesting user | `/teams/<id>` |

### Membership Changes

| `event_type` | Channels | Recipient | Redirect |
| :--- | :--- | :--- | :--- |
| `team_member_removed` | system + email | Removed user | `/teams/<id>` |
| `team_member_left` | system | Team captain | `/teams/<id>` |

---

## Message Tag Format

Notification messages may contain embedded interactive tags. The frontend parses them into clickable links.

| Tag | Renders as |
| :--- | :--- |
| `[user:{id}:{name}]` | Clickable link → `/users/{id}` |
| `[team:{id}:{name}]` | Clickable `router-link` → `/teams/{id}` |
| `[team:{id}:{name}:private]` | Greyed-out (unclickable) — team is private |
| `[team:{id}:{name}:public]` | Clickable `router-link` → `/teams/{id}` |

**Example message (raw):**
```
[user:7:john_doe] has sent a request to join team "[team:3:Alpha:public]".
```

---

## Channels

| Channel | Delivery | Configurable per user? |
| :--- | :--- | :--- |
| `system` | In-app notification center (database) | ✅ Yes |
| `email` | SMTP email with HTML template | ✅ Yes + global kill-switch |

Email messages use the HTML template at  
`notifications/templates/notifications/email_notification.html`.

---

## Settings API

### `GET /api/notifications/settings/`

Returns all available event types and the authenticated user's personal config.

```json
{
  "event_types": [
    { "key": "team_invitation_received", "title": "Team Invitation" }
  ],
  "configs": [
    {
      "event_type": "team_invitation_received",
      "is_system_enabled": true,
      "is_email_enabled": true
    }
  ],
  "global_config": {
    "emails_disabled_globally": false
  }
}
```

> Accessing this endpoint **auto-creates** default configs for any missing event types.

### `POST /api/notifications/settings/config/update/`

Enable or disable a specific channel for one event type.

```json
{
  "event_type": "team_invitation_received",
  "is_system_enabled": true,
  "is_email_enabled": false
}
```

### `POST /api/notifications/settings/global/update/`

Master switch — disables **all** email notifications regardless of per-event settings.

```json
{ "emails_disabled_globally": true }
```

---

## Adding a New Event Type

1. **`notifications/config.py`** — add a new `NotificationEvent` entry to `EVENTS`:
   ```python
   'my_new_event': NotificationEvent(
       key='my_new_event',
       channels=['system', 'email'],
       title='My Event Title',
       message='Something happened to [user:{user_id}:{user_name}].',
       email_subject='Something happened',
   ),
   ```

2. **`notifications/channels.py`** — add the event to `EVENT_TYPE_LABELS` and `EVENT_ACTION_LABELS` (and `_GENERAL_TEAMS_EVENTS` if it should redirect to `/teams` instead of `/teams/<id>`).

3. **Trigger it** from a Django signal or service:
   ```python
   from notifications.services import NotificationService

   NotificationService.notify(
       recipients=[user],
       event_type='my_new_event',
       context={'user_id': actor.id, 'user_name': actor.username},
   )
   ```

---

## Signal-Based Triggers (Teams App)

Team notifications are sent via Django signals defined in `teams/signals.py`.  
Receivers live in `notifications/signals.py` and call `NotificationService.notify()`.

| Signal | Fired from | Notification sent |
| :--- | :--- | :--- |
| `invitation_received` | `TeamInviteView.post` | `team_invitation_received` |
| `invitation_responded` | `TeamInvitationAccept/DeclineView` | `team_invitation_accepted/declined` |
| `join_request_received` | `TeamJoinRequestCreateView.post` | `team_join_request_received` |
| `join_request_responded` | `TeamJoinRequestAccept/DeclineView` | `team_join_request_accepted/declined` |
| `member_removed` | `TeamRemoveMemberView.post` | `team_member_removed` |
| `member_left` | `TeamLeaveView.post` | `team_member_left` |

---

## Frontend Queries (Vue / TanStack Query)

Located in `src/queries/notifications/index.ts`:

| Hook | Description |
| :--- | :--- |
| `useNotifications(page?, pageSize?)` | Fetch paginated notification list |
| `useUnreadCount()` | Fetch unread count (polls every 30s) |
| `useMarkAsRead()` | Mutation — mark single notification read |
| `useMarkAllAsRead()` | Mutation — mark all read |
| `useDeleteNotification()` | Mutation — delete single notification |
| `useDeleteAllNotifications()` | Mutation — delete all notifications |
| `useNotificationSettings()` | Fetch user's notification config |
| `useUpdateEventConfig()` | Mutation — toggle system/email per event |
| `useUpdateGlobalConfig()` | Mutation — toggle global email kill-switch |

---

## Environment Variables

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `EMAIL_HOST` | `smtp.gmail.com` | SMTP host |
| `EMAIL_PORT` | `587` | SMTP port |
| `EMAIL_USE_TLS` | `True` | TLS for SMTP |
| `EMAIL_HOST_USER` | — | Sender address |
| `EMAIL_HOST_PASSWORD` | — | SMTP password / app password |
| `SITE_URL` | `http://localhost:5173` | Base URL for email CTA links |
