# TODO

  - The current `shutdown_script.py` uses WebSocket middleware calls (version 1).
  - The `websockets` library can likely still be used, but the message format needs to be updated to JSON-RPC 2.0.
  - The `connect`, `auth.login`, and `system.shutdown` methods in `shutdown_script.py` need to be updated according to the new API specification. The function names are for now not changing.
  - Refer to the official TrueNAS documentation for details on the JSON-RPC 2.0 API and example code.
  - The API endpoint will change from `/websocket` to `/api/current` (this is not yet final).
  - We might switch to using the official TrueNAS API client instead of the `websockets` library (this is not yet final).
- Migrate the project to the TrueNAS JSON-RPC 2.0 API.