/usr/bin/influxdb-daemon -config=/opt/influxdb/shared/config.toml
sleep 30  # Probably too long but 5 didn't work.
curl -X POST 'http://localhost:8086/db?u=root&p=root' -d '{"name": "mon"}' 
curl -X POST 'http://localhost:8086/db/mon/users?u=root&p=root' -d '{"name": "mon_api", "password": "password"}'
curl -X POST 'http://localhost:8086/db/mon/users?u=root&p=root' -d '{"name": "mon_persister", "password": "password"}'
