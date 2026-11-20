# Runbook 2 - DiskAlmostFull (warning)

**Trigger:** disk_percent > 85% for 5+ minutes.
**Impact:** logs and database writes may fail if the disk reaches 100%.
**Owner:** infra-team. **Mode:** simulated.

## 1. Validate (read-only)
1. `df -h` - confirm which mount is full.
2. `du -sh /var/log/* | sort -h | tail` - find the biggest directories.
3. Check the growth trend (Day 15 analysis): hours until 100%?

## 2. Safe actions (need human approval first)
- Compress or rotate old logs with `logrotate` (after confirming they are backed up).
- Do NOT delete files by hand without approval; never touch database files.

## 3. Stop conditions / rollback
- Stop if usage is still rising after cleanup -> escalate for a disk expansion request.

## 4. Escalation
- If > 95% -> treat as critical, page infra on-call.

## 5. Verify and close
- Disk < 75% and growth rate understood; add a note to the capacity memo.
