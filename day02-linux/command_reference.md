# Linux Command Reference (Day 2)

Environment: Kali Linux 6.6.15 in VirtualBox, 2 CPU cores, about 1 GB RAM.
Values in the last column come from my own baseline run on 20 Nov 2026 (`baseline_report.txt`).
Cells marked **[fill in]** are for you to run and complete yourself.

| Area | Command | What it reveals | What to look for | On my VM |
|---|---|---|---|---|
| Navigation | `pwd` | Current directory | Am I in the project folder? | `/home/ankit/Desktop/AIop/aiops-internship` |
| Navigation | `ls -la` | Files with size, owner, permissions, hidden files | Unexpected size 0 files, wrong owner | **[fill in]** |
| Navigation | `find . -name "*.py"` | Files matching a pattern | Where a file really is | **[fill in]** |
| Processes | `ps aux --sort=-%mem \| head` | Processes sorted by memory use | One process using most RAM | Firefox about 15% of memory |
| Processes | `top` (quit with `q`) | Live CPU and memory per process, load average | High %CPU, load vs core count | **[fill in]** |
| Processes | `kill <PID>` | Stops a process | Only use on your own test process | **[fill in]** (use a test `sleep 300` process) |
| Memory | `free -h` | RAM and swap used / available | Low "available", heavy swap use | 970 MiB total, 395 MiB available, swap 605 of 974 MiB used |
| Memory | `vmstat 1 5` | Memory, swap and CPU activity over 5 seconds | Non-zero `si/so` = swapping | **[fill in]** |
| Disk | `df -h` | Space used per filesystem | Use% above 85% | `/` is 89% (14G of 16G) |
| Disk | `du -sh *` | Size of each folder | What is taking the space | `/usr` about 12G of the 14G |
| Network | `ip a` | Network interfaces and IP addresses | Interface up, expected address | **[fill in]** |
| Network | `ss -tuln` | Listening TCP/UDP ports | Unexpected open ports | Only a DHCPv6 UDP port (546), no web or SSH service |
| Network | `ping -c 3 127.0.0.1` | Whether a host answers, and how fast | Packet loss, high time | **[fill in]** |
| Services | `systemctl status ssh` | State of a service | active / inactive / failed | **[fill in]** |
| Services | `journalctl -n 50` | Last 50 system log lines | Errors and warnings | Journals use about 160 MB |
| System | `uname -a` | Kernel and architecture | OS version | Linux 6.6.15 Kali, x86_64 |
| System | `uptime` | Time since boot, load average (1, 5, 15 min) | Load above the core count | Load 2.03, 2.23, 2.36 on 2 cores (busy) |
| System | `lscpu` | CPU model and core count | Number of cores | 2 cores, Intel i3 M 380 @ 2.53 GHz |

## Baseline observations (from my own data)
- Load average about 2 on 2 cores means the CPU is close to fully used.
- Memory is tight and swap is heavily used; Firefox is the largest process.
- `/` is 89% full, but the cause is installed software (12G in `/usr`), not growth - so a static 85% alert would fire on a disk that is not actually filling up. This is why Day 15 uses a growth trend.
- No web or SSH service is listening, which is good for a lab machine.

## My baseline note (write 5-6 lines yourself)
> Write here, in your own words: what is normal on this VM, what worries you, and how this baseline will be used later. Mention that Firefox was open, so this is not a fully idle baseline.
