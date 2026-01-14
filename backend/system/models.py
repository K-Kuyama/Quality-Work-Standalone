from django.db import models

# ファイルをアップロードするためのテーブル
# DatabaseUploadViewで使われる

class DBUpdateHistory(models.Model):
    fileName = models.CharField(max_length=128)
    uploadTime = models.DateTimeField()
    contents = models.FileField(upload_to=".")
    status = models.CharField(max_length=128)

class QwMeta(models.Model):
    key = models.CharField(max_length=64)
    value = models.CharField(max_length=64)
