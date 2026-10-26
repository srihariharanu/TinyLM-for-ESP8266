# Offline HTTP API

Experimental API at http://192.168.4.1/; current implementation: portal.h.
POST bodies use application/x-www-form-urlencoded. Responses are JSON except
the gzip HTML page and captive redirects. Browser cookies identify sessions.
This local API has no TLS or strong identity authentication.

| Method | Path | Request | Success |
| --- | --- | --- | --- |
| GET | / | Local host address | 200 gzip HTML |
| GET | /api/status | None | ready, freeHeap, stations, busy |
| GET | /api/session | Optional cookie | signedIn, ready, optional name |
| POST | /api/signin | name, 1–32 printable ASCII characters | 200 name and TinyLM cookie |
| POST | /api/signout | Cookie | 200 ok; clears session/cookie |
| POST | /api/chat | Cookie; message, 1–120 printable ASCII characters | 202 id and generating state |
| GET | /api/result?id=NUMBER | Same session cookie and job ID | 200 state and partial/final reply |

Poll results until state is done. Only the current job belongs to a session;
previous results are replaced. There is one active generation across sessions.
Errors: 400 invalid input/ID, 401 missing session, 404 unknown endpoint or
unavailable reply, 409 busy, 503 starting or no available sessions. Error JSON
contains error text. Unknown non-API paths redirect to the local page. Sessions
expire after 30 minutes; device restart clears them. Do not log session tokens.

Project maintainer and original-work rights holder: **Sri Hariharan U**.
Rights contact: **srihariharanu@gmail.com**.
