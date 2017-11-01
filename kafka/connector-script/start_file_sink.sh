bin/connect-standalone.sh conf/connect-standalone.properties conf/connect-file-sink.properties > /tmp/file-sink.log 2>1 &
tail -f /tmp/file-sink.log

