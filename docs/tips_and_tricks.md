# Tips & Tricks

## Synchronizing containers time with host time

If you want to synchronize containers' time with the time of the host they
are running on, you need to add to every service the following
volumes:

```yaml
volumes:
  - "/etc/timezone:/etc/timezone:ro"
  - "/etc/localtime:/etc/localtime:ro"
```
