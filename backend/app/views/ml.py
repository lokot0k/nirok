import os
import shutil
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

from app.models.ml_model import get_predicts
from app.utils.storage import MyStorage


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
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            requ = request.FILES['docfile']
            storage = MyStorage()
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
