# HealthCheck - Scheduler

## `POST` - `/scheduler`

Creates a new scheduler for the given check to run every T interval (minutes).

Body example:

```json
// /scheduler
{
    "check_id": "d9bd2ce6-9aa2-4145-bcbb-4ba8aca489b9",
    "interval": 15 // 15 minutes
}
```

The example above is to create a scheduler to run every 15 minutes.

## `GET` - `/scheduler`

Returns all schedulers created.

Example:

```json
[
    {
        "key": "d9bd2ce6-9aa2-4145-bcbb-4ba8aca489b9",
        "enable": true,
        "valid": true
    },
    {
        "key": "40d9bd2ce6-9aa2-4145-bcbb-4ba8aca489b9",
        "enable": true,
        "valid": true
    }
]
```

## `DELETE` - `/scheduler/<check_id>`

Deletes the scheduler for the given check id.
