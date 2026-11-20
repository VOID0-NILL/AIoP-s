# Log findings

- Records parsed: **9115** (malformed lines skipped: 0)
- Time range: 2026-11-20 00:00:05.507000 to 2026-11-20 23:59:20.818000
- Level counts: {'INFO': 7587, 'WARN': 879, 'ERROR': 649}

## Errors by service
service
fee-service    284
web-server     183
app-server     182

## Top 5 error patterns
pattern
502 Bad Gateway /fee/pay                        157
Connection pool exhausted (max=20)              143
DB connection timeout after 30s                 141
Upstream fee-service returned 500               139
Request timeout calling notification-service     43

## Errors per 10-minute window (top 6)
timestamp
2026-11-20 14:10:00    128
2026-11-20 14:30:00    127
2026-11-20 14:20:00    123
2026-11-20 14:40:00    120
2026-11-20 14:50:00     52
2026-11-20 14:00:00     34

## Noisiest repeated messages (all levels, top 5)
pattern
GET /home 200 <N>ms                               1597
User login success user_id=<ID>                   1509
GET /results/<ID> 200 <N>ms                       1499
Session created user_id=<ID>                      1498
Fee payment accepted user_id=<ID> amount=15000    1483

## Limitations
- Synthetic data: one injected incident, so patterns are cleaner than real logs.
- Pattern grouping uses simple regex; unseen formats would stay ungrouped.