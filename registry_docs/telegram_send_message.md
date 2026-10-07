# telegram_send_message

Send a Telegram message. Requires confirm=true.

The gateway injects `credentials_json` from the connected account. Do not invent a token or paste a secret into the arguments.

## Parameters

| Name | Required | Meaning |
|---|---|---|
| `chat_id` | yes | Chat id or @username |
| `text` | yes | Message text |
| `confirm` | no | bool |
| `dry_run` | no | bool |

## Cases

### Typical call

Input:

```json
{
  "chat_id": "example-id",
  "text": "hello",
  "dry_run": true
}
```

Output:

```json
{
  "success": true,
  "result": "completed"
}
```

### Missing `chat_id`

The tool rejects the call and does not guess the missing value.

Input:

```json
{
  "text": "hello",
  "dry_run": true
}
```

Output:

```json
{
  "success": false,
  "error": {
    "error_code": "invalid_argument",
    "error_message": "chat_id is required",
    "retryable": false
  }
}
```

### Preview the write

Set `dry_run` to true. The tool returns the planned change and does not send it.

Input:

```json
{
  "chat_id": "example-id",
  "text": "hello",
  "dry_run": true
}
```

### Confirmed write

Set `confirm` to true. Omit `dry_run`.

Input:

```json
{
  "chat_id": "example-id",
  "text": "hello",
  "confirm": true
}
```

### Write without confirm or dry_run

Input:

```json
{
  "chat_id": "example-id",
  "text": "hello"
}
```

Output:

```json
{
  "success": false,
  "error_message": "confirm=true required for write tools (or dry_run=true to preview)"
}
```
