import json
import os
import shutil
import time
from collections import defaultdict

from django.core.files.base import ContentFile
from django.db import models
from django.forms import forms
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views import View
from django.conf import settings
import zipfile
import csv
from PIL import Image
import cv2

from app.models.ml_model import get_predicts
from app.utils.storage import MyStorage


def convert_avi_to_mp4(avi_file_path, output_path):
    os.system(
        "ffmpeg -i '{input}' -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 '{output}'".format(
            input=avi_file_path, output=output_path))
    return True


def extract_first_frame(mp4_file_path, output_path):
    vidcap = cv2.VideoCapture(str(mp4_file_path))
    success, image = vidcap.read()
    if success:
        cv2.imwrite(str(output_path), image)


class DocumentForm(forms.Form):
    docfile = forms.FileField(label='Select a file')


class Document(models.Model):
    docfile = models.FileField(upload_to='documents/abc.zip')


class MlView(View):
    def get(self, request: HttpRequest, *args,
            **kwargs) -> JsonResponse | HttpResponse:
        storage = MyStorage()
        d = defaultdict(list)
        with open(storage.path('submission.csv'), 'r') as f:
            reader = csv.reader(f, delimiter=",")
            next(reader)  # пропускаем хедер
            for row in reader:
                at_id = row[0]
                class_ind = row[1]
                d[class_ind].append(at_id)
        d = dict(d)
        return JsonResponse(d)

    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        storage = MyStorage()
        f = open(storage.path('pgb.json'), 'w')
        json.dump({"i": 0, "l": 10, "s": "Скачиваем файлы..."}, f)
        f.close()
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            requ = request.FILES['docfile']
            shutil.rmtree(settings.MEDIA_ROOT)
            settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
            path = storage.save('abc.zip',
                                ContentFile(requ.read()))

            # разархивировать по path, грузануть в медиа. Собрать .csv в едины жсон респонс.
            with zipfile.ZipFile(path,  # выгрузка
                                 "r") as zip:
                zip.extractall(settings.MEDIA_ROOT)

            directory = os.fsencode(
                settings.MEDIA_ROOT)  # возможно пригодиться в будущем

            # конвертить avi в mp4
            for video in os.listdir(directory):
                video_name = video.decode('utf-8')
                if video_name.lower().endswith(".avi"):
                    convert_avi_to_mp4(settings.MEDIA_ROOT / video_name,
                                       settings.MEDIA_ROOT / video_name.replace('.avi', '.mp4'))
                    # os.remove(settings.MEDIA_ROOT / video_name)

            for video in os.listdir(directory):
                video_name = video.decode('utf-8')
                if video_name.lower().endswith(".mp4"):
                    extract_first_frame(settings.MEDIA_ROOT / video_name,
                                        settings.MEDIA_ROOT / video_name.replace('.mp4', '.jpg'))

            get_predicts(os.listdir(directory), True)  ##  СПИСОК
            d = defaultdict(list)
            with open(storage.path('submission.csv'), 'r') as f:
                reader = csv.reader(f, delimiter=",")
                next(reader)  # пропускаем хедер
                for row in reader:
                    at_id = row[0]
                    class_ind = row[1]
                    d[class_ind].append(at_id)
            d = dict(d)
            d.update({"success": "true"})
            d.update({"csv": "/media/submission.csv"})
            return JsonResponse(d)
        else:
            return JsonResponse({"success": "false", "message": "плохо"},
                                status=403)

    def head(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'message': 'unsupported method'}, status=403)

    def put(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'me ssage': 'unsupported method'}, status=403)
