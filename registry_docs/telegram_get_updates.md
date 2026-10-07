# telegram_get_updates

Get recent Telegram bot updates (long-poll replacement for v1).

The gateway injects `credentials_json` from the connected account. Do not invent a token or paste a secret into the arguments.

## Parameters

| Name | Required | Meaning |
|---|---|---|
| `limit` | no | int |
| `offset` | no | Optional[int] |

## Cases

### Typical call

Input:

```json
{}
```

Output:

```json
{
  "success": true,
  "result": "completed"
}
```
