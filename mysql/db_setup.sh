/usr/sbin/mysqld &
sleep 5
mysql -uroot -ppassword < /chef/mon.sql
