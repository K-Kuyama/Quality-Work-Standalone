from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

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
    
# 音声イベントデータ
# selected 0:start  1:longest  2: another

class AudioActivity(models.Model):
    start_time = models.DateTimeField(unique=True)
    end_time = models.DateTimeField(unique=True)
    duration = models.IntegerField()
    start_app = models.CharField(max_length=128)
    start_title = models.CharField(max_length=256)
    longest_app = models.CharField(max_length=128, null=True)
    longest_title = models.CharField(max_length=256, null=True)
    another_app = models.CharField(max_length=128, default = None, null=True)
    another_title = models.CharField(max_length=256, default = None, null=True)
    selected = models.IntegerField(default = 0,
                                validators=[MinValueValidator(0),
                                MaxValueValidator(2)])
    #show_front = models.BooleanField(default=True)
    show_policy = models.IntegerField(default = 0,
                                validators=[MinValueValidator(0),
                                MaxValueValidator(2)])


# システム設定データ
# audio_activity_policy  0:無効 1:Audio優先 2:Window優先 3:個別設定

class SystemSettings(models.Model):
    role = models.CharField(max_length=32, default="default")
    audio_activity_policy = models.IntegerField(default=0,
                                validators=[MinValueValidator(0),
                                MaxValueValidator(3)])
    duration_threshold = models.IntegerField(default=10)
    strokes_threshold = models.IntegerField(default=10)
    distance_threshold = models.IntegerField(default=1000)

