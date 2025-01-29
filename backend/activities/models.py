from django.db import models

# Create your models here.
class Activity(models.Model):
    start_time = models.DateTimeField(unique=True)
    duration = models.IntegerField()
    distance_x = models.FloatField()
    distance_y = models.FloatField()
    strokes = models.IntegerField()
    scrolls = models.IntegerField()
    app = models.CharField(max_length=128)
    title = models.CharField(max_length=256)

# 以下、カテゴライズ用のユーザ設定データ
    
class Perspective(models.Model):
    name = models.CharField(max_length=128)
    color = models.CharField(max_length=128)
    use_def_color= models.BooleanField()
    categorize_model = models.CharField(max_length=128, null=True)
    
class Category(models.Model):
    perspective = models.ForeignKey(Perspective, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=128)
    color = models.CharField(max_length=128)
    
class CategorizedActivity(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="activities")
    app = models.CharField(max_length=128)
    title = models.CharField(max_length=256)
    
class CategorizedKeyWord(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="key_words")
    word = models.CharField(max_length=128)
    positive = models.BooleanField()
    
# データアップロード用の管理テーブル

def set_upload_to(instance, filename):
    print(f"user_id:{str(instance.user_id)}")
    print(f"filename:{filename}")
    return "sc{0}/{1}".format(str(instance.user_id), filename)

class FileUpdateHistory(models.Model):
    #ファイルアップロード先のフォルダ名を決定するためにuser idを使う
    #user_id = models.IntegerField()
    fileName = models.CharField(max_length=128)
    uploadTime = models.DateTimeField()
    contents = models.FileField(upload_to=".")
    #contents = models.FileField(upload_to=set_upload_to)
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
    dataCount = models.IntegerField()
    status = models.CharField(max_length=128)
    

    