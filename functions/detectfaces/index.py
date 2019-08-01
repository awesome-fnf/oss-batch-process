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

  cascPath = "/code/haarcascade_frontalface_default.xml"

  # Create the haar cascade
  faceCascade = cv2.CascadeClassifier(cascPath)

  # Read the image
  image = cv2.imread(imagePath)
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  # Detect faces in the image
  faces = faceCascade.detectMultiScale(
      gray,
      scaleFactor=1.1,
      minNeighbors=3,
      minSize=(30, 30),
      flags=cv2.CASCADE_SCALE_IMAGE
  )

  logger.info("Found %d faces!", len(faces))

  # Draw a rectangle around the faces
  for (x, y, w, h) in faces:
      cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

  # write the image to a file
  cv2.imwrite(newImagePath, image)
  
  # upload
  bucket.put_object_from_file("face-detection/" + evt["key"], newImagePath)

  return {"faces": len(faces)}