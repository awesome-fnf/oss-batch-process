# -*- coding: utf-8 -*-
import logging
import cv2
import sys
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
  tmpdir = '/tmp/download/'
  imagePath = tmpdir + "old"
  newImagePath = tmpdir + "new.jpg"
  
  os.system("rm -rf /tmp/*")
  os.mkdir(tmpdir)
  
  #download
  bucket.get_object_to_file(evt["key"] , imagePath)

  # Read the image
  image = cv2.imread(imagePath)
  res = cv2.resize(image, dsize=(evt["width"], evt["height"]), interpolation=cv2.INTER_CUBIC)

  # write the image to a file
  cv2.imwrite(newImagePath, res)
  
  # upload
  bucket.put_object_from_file("thumbnails/" + evt["key"], newImagePath)

  return {}