# First postfix needs to be running, the image is set to use local postfix
/etc/init.d/postfix start

# If kafka just started often the notification engine starts before it is ready, in which case retry
start=`date "+%s"`
/usr/local/bin/monasca-notification
duration=$[ `date "+%s"` - $start ]
if [ $duration -lt 60 ]; then
  sleep 60
  /usr/local/bin/monasca-notification
fi
