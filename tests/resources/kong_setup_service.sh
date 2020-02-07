#!/usr/bin/env sh

sleep 3

curl -i -X POST \
  --url http://testleo-kong-service:8001/services/ \
  --data 'name=testleo-main-service' \
  --data 'url=http://testleo-main-service:5000'

curl -i -X POST \
  --url http://testleo-kong-service:8001/services/testleo-main-service/routes \
  --data 'paths[]=/app'
