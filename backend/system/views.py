from django.shortcuts import render
from django.db import connection
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework import serializers

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from activities.decolators import attach_decorator
from django.conf import settings
import sqlite3
import re
import os
import shutil

from system.models import DBUpdateHistory
if settings.QT_MULTI:
    from tenant_schemas.storage import TenantFileSystemStorage

class DatabaseUploadSerializer(serializers.ModelSerializer):
    # アップロードされた情報を受け取って格納する時に使われるシリアライザー

    class Meta:
            model = DBUpdateHistory
            fields = ('fileName', 'uploadTime', 'contents', 'status')

class DatabaseUploadResultSerializer(serializers.Serializer):
    # 情報を格納後、格納された情報（結果）を返す時に使われるシリアライザー

    path = serializers.CharField(max_length=128)
    f_id = serializers.IntegerField()

class DatabaseUploadView(generics.ListCreateAPIView):
    # データベースファイルをアップロードする

    queryset = DBUpdateHistory.objects.all()
    serializer_class = DatabaseUploadSerializer
    if settings.QT_MULTI:
        # セッション認証ができている場合にアクセスを許可する
        authentication_classes = (SessionAuthentication,)
        permission_classes = (IsAuthenticated, )
    

    def urlToFile(self, url_str):
        # データベースに格納されているファイルのURLをファイルパスに変換する
        MEDIA_ROOT = getattr(settings, "MEDIA_ROOT", None)
        MEDIA_URL = getattr(settings, "MEDIA_URL", None)
        #print(f"re.search({MEDIA_URL},{url_str})")
        ro = re.search(MEDIA_URL, url_str)
        t_str = url_str[ro.span()[1]:]
        file_str = os.path.join(MEDIA_ROOT, t_str)
        #print(file_str)
        return file_str
    

    def get_result_serializer(self, *args, **kwargs):
        """
        結果を返すシリアライザーを返す
        """
        serializer_class = DatabaseUploadResultSerializer
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        #print("post method called")
        return self.create(request, *args, **kwargs)
    
    
    def create(self, request, *args, **kwargs):
        #print(f"request data:{request.data}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # データベースにデータを書き込む
        self.perform_create(serializer)
        # データインポート
        # contentsに格納されているURLを、ファイルパスに変換する
        f_name = self.urlToFile(serializer.data['contents'])
        #print(serializer.instance)
        id = serializer.instance.id
        r_data = {"path": f_name, "f_id": id}
        r_serializer = self.get_result_serializer(data = r_data)
        r_serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(r_serializer.data)
        return Response(r_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

class DBUpdateHistoryViewSet(viewsets.ModelViewSet):
    # DBアップデートテーブル用ビューセット
    # エントリーの削除用に使う

    queryset = DBUpdateHistory.objects.all()
    serializer_class = DatabaseUploadSerializer

    def get_file_path(self):
        params = self.request.query_params
        if 'f_path' in params:
            return params.get('f_path')
        else:
            return None

    def perform_destroy(self, instance):
        instance.delete()
        file_path = self.get_file_path()
        if file_path:
            os.remove(file_path)

class DBUpdateHistoryClearView(generics.ListAPIView):
    # DBアップデートテーブルにあるエントリーを全てクリアする
    queryset = DBUpdateHistory.objects.all()

    def urlToFile(self, url_str):
        # データベースに格納されているファイルのURLをファイルパスに変換する
        MEDIA_ROOT = getattr(settings, "MEDIA_ROOT", None)
        MEDIA_URL = getattr(settings, "MEDIA_URL", None)
        ro = re.search(MEDIA_URL, url_str)
        t_str = url_str[ro.span()[1]:]
        file_str = os.path.join(MEDIA_ROOT, t_str)
        return file_str

    @attach_decorator(settings.QT_MULTI,method_decorator(login_required)) 
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        for entry in queryset:
            file_path = self.urlToFile(entry.contents.url)
            # アップロードされているファイルを消去
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        # エントリーを全て消去
        DBUpdateHistory.objects.all().delete()
        return Response([])

# DatabaseInfoViewのためのSerializer
class DatabaseInfoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    count = serializers.IntegerField()
    parents = serializers.CharField(max_length=128)
    children = serializers.CharField(max_length=128)
    replace = serializers.BooleanField()


class DatabaseInfoView(generics.ListAPIView):
    # アップロードされたソース側データベース情報の取得
    file = settings.BASE_DIR / "db.sqlite3"
    serializer_class = DatabaseInfoSerializer

    def evaluate_params(self):
        params = self.request.query_params
        if 'file' in params:
            self.file = params.get('file')

    def getTableName(self, target):
        target_list = target.split(".")
        return target_list[0].lower() +"_"+target_list[1].lower()

    @attach_decorator(settings.QT_MULTI,method_decorator(login_required)) 
    def list(self, request, *args, **kwargs):
        # tablesは移行対象になり得るテーブルの情報。以下の内容が含まれる
        # (テーブル名,依存している親テーブルのインデック、依存している子テーブルのインデックス、完全置き換えか否かのデフォルト値)
        tables = [("activities.Activity",None, None, False), ("activities.Perspective",None, "2-3-4", True), 
                  ("activities.Category","1", "3-4", True),("activities.CategorizedKeyWord","1-2", None, True), 
                  ("activities.CategorizedActivity","1-2", None, True),
                  ("activities.AudioActivity",None, None, False),
                  ("activities.ActivityPredictor",None, None, False),
                  ("activities.SystemSettings",None, None, True)
                  ]
        results = []
        self.evaluate_params()
        #print(f"db file is {self.file}")
        try:
            conn = sqlite3.connect(self.file)
            cur = conn.cursor()
            for table in tables:
                table_name = self.getTableName(table[0])
                select_sql = "SELECT count(*) FROM "+table_name
                try:
                    cur.execute(select_sql)
                    count = cur.fetchone()
                    results.append({"name": table[0], "count": count[0], 
                                    "parents": table[1], "children": table[2], "replace": table[3]})
                except sqlite3.OperationalError as ex:
                    print(f"{self.file}:{table[0]} error {ex}")
        except sqlite3.Error as e:
            print(f"{self.file} error {e}")
        if 'file' in request.query_params:
            conn.close()
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)


from django.core import management
from django.core.management.commands import loaddata
from rest_framework import status
from .DataExporter import DataExporter

# management.call_command("flush", verbosity=0, interactive=False)
# management.call_command("loaddata", "test_data", verbosity=0)
# management.call_command(loaddata.Command(), "test_data", verbosity=0)



        
class TableMigrationSerializer(serializers.Serializer):
    target = serializers.CharField(max_length=128)
    result = serializers.CharField(max_length=128)

class TableMigrationView(generics.ListAPIView):
    # 指定されたソースデータベースファイルから指定されたテーブルをデータベースに書き込む
    file = None
    table = None
    replace = False
    serializer_class = TableMigrationSerializer

    target_info = {
        "activities.Activity":["id", "start_time", "duration", "distance_x", "distance_y", 
                                    "strokes", "scrolls", "app", "title"],
        "activities.Perspective": ["id", "name", "color", "use_def_color", "categorize_model", "index"],
        "activities.Category": ["id", "name", "color", "perspective", "index"],
        "activities.CategorizedActivity": ["id", "app", "title", "category"],
        "activities.CategorizedKeyWord": ["id", "word", "positive", "category"],
        "activities.AudioActivity": ["id", "start_time", "end_time", "duration", "start_app", "start_title",
                                     "longest_app", "longest_title", "another_app", "another_title",
                                     "selected", "show_policy"],
        "activities.ActivityPredictor": ["id", "p_id", "name", "created_dtime", 
                                         "num_of_labels", "num_of_learning_data", "score", "using", "data_start", "data_end"],
        "activities.SystemSettings": ["id", "role", "audio_activity_policy", "duration_threshold",
                                      "strokes_threshold", "distance_threshold"]
    }


    def evaluate_params(self):
        #print(f"->{self.request.query_params}")
        params = self.request.query_params
        if 'file' in params:
            self.file = params.get('file')
        if 'table' in params:
            self.table = params.get('table')
        if 'replace' in params:
            if params.get('replace').lower() == "true":
                self.replace = True


    @attach_decorator(settings.QT_MULTI,method_decorator(login_required)) 
    def list(self, request, *args, **kwargs):
        self.evaluate_params()
        de = DataExporter()
        de.connect(self.file)
        #print(f"self.table = {self.table}")
        r = de.writeTableData(self.table, self.target_info[self.table], self.replace)
        results={"target":self.table, "result":r}
        de.close()
        serializer = self.get_serializer(results)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class InitDBView(generics.ListAPIView):
    # データベースを初期化。djangoのコマンドflushとloaddata(fixtureのロード)を実行する。
    # 加えてAI関連のファイルを消去する
    @attach_decorator(settings.QT_MULTI,method_decorator(login_required)) 
    def list(self, request, *args, **kwargs):
        sts = status.HTTP_202_ACCEPTED
        result = "success"
        # データベースの初期化
        fixture = os.path.join(settings.BASE_DIR, 'fixture.json')
        try:
            if settings.QT_MULTI:
                # 念の為、データベースの接続先をtenant.schema_nameに設定
                connection.set_schema(request.tenant.schema_name)
            management.call_command("flush", "--noinput")
            management.call_command("loaddata", fixture)
        except Exception as e:
            result = repr(e)
            sts = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(result, status = sts)
        # ファイル群の消去
        predictors_dir = os.path.join(settings.MEDIA_ROOT, "predictors")
        if settings.QT_MULTI:
            storage = TenantFileSystemStorage()
            predictors_dir = storage.path("predictors")
        try:
            shutil.rmtree(predictors_dir)
        except Exception as e:
            result = repr(e)
            sts = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(result, status = sts)
        return Response(result, status = sts)


