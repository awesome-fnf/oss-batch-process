# -*- coding: utf-8 -*-
import oss2
import json
import os
import logging


def handler(event, context):
  logger = logging.getLogger()
  evt = json.loads(event)
  logger.info("Handling event: %s", evt)
  creds = context.credentials
  endpoint = os.environ['OSS_ENDPOINT']
  if creds.security_token != None:
    auth = oss2.StsAuth(creds.access_key_id, creds.access_key_secret, creds.security_token)
  else:
    # for local testing, use the public endpoint
    endpoint = str.replace(endpoint, "-internal", "")
    auth = oss2.Auth(creds.access_key_id, creds.access_key_secret)

  bucket = oss2.Bucket(auth, endpoint, evt["bucket"])
  result = bucket.list_objects(prefix = evt["prefix"], marker =  evt["marker"], delimiter = evt["delimiter"], max_keys = 100)
  keys = []
  for obj in result.object_list:
    keys.append(obj.key)
  logger.info("Found %d objects", len(keys))

  return {
    "keys": keys,
    "hasMore": result.is_truncated,
    "marker": result.next_marker
  }
