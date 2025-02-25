#!/bin/bash
# init_script.sh
until [ -f /opt/zeppelin/conf/interpreter.json ]; do
  echo 'Waiting for file...'
  sleep 1
done


echo '[INIT SCRIPT] File exists, proceeding with flink remote configs...'

# Ensure the file has the correct permissions
chmod 666 /opt/zeppelin/conf/interpreter.json

echo '[INIT SCRIPT] flink.execution.mode'
# Update flink.execution.mode value
sed -i 's/"flink.execution.mode": {[^}]*"value": "[^"]*"/"flink.execution.mode": { "name": "flink.execution.mode", "value": "remote", "type": "string", "description": "Execution mode, it could be local|remote|yarn" }/' /opt/zeppelin/conf/interpreter.json
if [ $? -ne 0 ]; then
  echo '[INIT SCRIPT] Error updating flink.execution.mode'
  exit 1
fi

echo '[INIT SCRIPT] flink.execution.remote.host'
# Update flink.execution.remote.host value
sed -i 's/"flink.execution.remote.host": {[^}]*"value": "[^"]*"/"flink.execution.remote.host": { "name": "flink.execution.remote.host", "value": "flink-jobmanager", "type": "string", "description": "Host name of running JobManager. Only used for remote mode" }/' /opt/zeppelin/conf/interpreter.json
if [ $? -ne 0 ]; then
  echo '[INIT SCRIPT] Error updating flink.execution.remote.host'
  exit 1
fi

echo '[INIT SCRIPT] flink.execution.remote.port'
# Update flink.execution.remote.port value
sed -i 's/"flink.execution.remote.port": {[^}]*"value": "[^"]*"/"flink.execution.remote.port": { "name": "flink.execution.remote.port", "value": "8081", "type": "number", "description": "Port of running JobManager. Only used for remote mode" }/' /opt/zeppelin/conf/interpreter.json
if [ $? -ne 0 ]; then
  echo '[INIT SCRIPT] Error updating flink.execution.remote.port'
  exit 1
fi

echo 'Finished'
