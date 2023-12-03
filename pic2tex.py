#!/usr/bin/env python
import requests
import json

import dotenv

def load_secrets():
  return dotenv.dotenv_values(".env")

def image_request(image):
  secrets = load_secrets()

  r = requests.post("https://api.mathpix.com/v3/text",
      files={"file": open(image,"rb")},
      data={
        "options_json": json.dumps({
        "math_inline_delimiters": ["$", "$"],
        "include_word_data": True
        })
      },
      headers={
        "app_id": secrets["app_id"],
        "app_key": secrets["app_key"],
      }
  )

  return r.json()

if __name__ == "__main__":
  load_secrets()

