#export CLASSPATH=/opt/connectors/*
bin/connect-standalone.sh conf/connect-standalone.properties conf/quickstart-hdfs.properties > /tmp/hdfs-sink.log 2>1 &
tail -f /tmp/hdfs-sink.log

