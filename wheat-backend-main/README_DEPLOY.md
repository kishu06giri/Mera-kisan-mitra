Wheat Classifier FastAPI

Deploy steps (Render / Railway / DigitalOcean / Heroku):

- Create repo and push these files.
- On the host provider, set env var GDRIVE_ID (Google Drive file id of your wheat_classifier.pth).
  Or upload the model to repo (not recommended) and set MODEL_PATH accordingly.
- Start command (if not using Docker):
  uvicorn app:app --host 0.0.0.0 --port $PORT

Render Docker: choose Docker option and deploy.
