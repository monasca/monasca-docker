# Tips & Tricks

## Synchronizing containers time with host time

If you want to synchronize containers time with host time they
are running on, you need to add to every service following
volumes:

```yaml
volumes:
  - "/etc/timezone:/etc/timezone:ro"
  - "/etc/localtime:/etc/localtime:ro"
```
