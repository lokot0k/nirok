import csv
import io
import json
import os
import shutil
from collections import defaultdict

from PIL import Image
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views import View
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

from googleapiclient.http import MediaIoBaseDownload
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from oauth2client.client import GoogleCredentials

from app.models.ml_model import get_predicts
from app.utils.drive_downloader import download_files, createRemoteFolder, \
    moveFile
from app.utils.storage import MyStorage
from app.views.ml import convert_avi_to_mp4, extract_first_frame
from djangoProject import settings


class MlDiskView(View):
    def get(self, request: HttpRequest, *args,
            **kwargs) -> JsonResponse | HttpResponse:
        pass

    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        creds = None
        SCOPES = ['https://www.googleapis.com/auth/drive']
        st = MyStorage()
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(settings.STATIC_ROOT / "token.json"):
            creds = Credentials.from_authorized_user_file(
                settings.STATIC_ROOT / "token.json",
                SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.STATIC_ROOT / "client_secret.json", SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(settings.STATIC_ROOT / "token.json", 'w') as token:
                token.write(creds.to_json())

        service = build('drive', 'v3', credentials=creds)
        folder_id = json.loads(request.body)['folder']  # request.body.folder
        shutil.rmtree(settings.MEDIA_ROOT)
        settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        names = ["cartwheel", "catch", "clap", "climb", "dive", "draw_sword",
                 "dribble", "fencing", "flic_flac", "golf",
                 "handstand", "hit", "jump", "pick", "pour", "pullup", "push",
                 "pushup", "shoot_ball", "sit", "situp", "swing_baseball",
                 "sword_exercise", "throw"]
        folders = dict()
        for i in names:
            folders.update({i: createRemoteFolder(service, i, folder_id)})
        f = open(st.path('pgb.json'), 'w')
        json.dump({"i": 0, "l": 10, "s": "Скачиваем файлы..."}, f)
        f.close()
        down = download_files(service, folder_id, st.path(""))
        storage = MyStorage()
        directory = os.fsencode(
            settings.MEDIA_ROOT)  # возможно пригодиться в будущем

        # конвертить avi в mp4
        for video in os.listdir(directory):
            video_name = video.decode('utf-8')
            if video_name.lower().endswith(".avi"):
                convert_avi_to_mp4(settings.MEDIA_ROOT / video_name,
                                   settings.MEDIA_ROOT / video_name.replace(
                                       '.avi', '.mp4'))

        for video in os.listdir(directory):
            video_name = video.decode('utf-8')
            if video_name.lower().endswith(".mp4"):
                extract_first_frame(settings.MEDIA_ROOT / video_name,
                                    settings.MEDIA_ROOT / video_name.replace(
                                        '.mp4', '.jpg'))

        get_predicts(os.listdir(directory), True)  ##  СПИСОК
        d = defaultdict(list)
        l = len(down.values())
        i = 0
        f = open(st.path('pgb.json'), 'w')
        json.dump({"i": 0, "l": l, "s": "Расфасовываем файлы..."}, f)
        f.close()
        with open(storage.path('submission.csv'), 'r') as f:
            reader = csv.reader(f, delimiter=",")
            next(reader)  # пропускаем хедер
            for row in reader:
                i += 1
                f = open(st.path('pgb.json'), 'w')
                json.dump({"i": i, "l": l, "s": "Расфасовываем файлы..."}, f)
                f.close()
                at_id = row[0]
                class_ind = row[1]
                moveFile(service, down[at_id.replace('.mp4', '.avi')],
                         folders[class_ind])
                d[class_ind].append(at_id)
        d = dict(d)
        d.update({'success': 200})
        f = open(st.path('pgb.json'), 'w')
        json.dump({"i": 0, "l": l, "s": "Скачиваем файлы..."}, f)
        f.close()
        return JsonResponse(d)

    def head(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'message': 'unsupported method'}, status=403)

    def put(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'me ssage': 'unsupported method'}, status=403)
