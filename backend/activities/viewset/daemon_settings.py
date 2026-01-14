'''
Created on 2025/05/17

@author: kuyamakazuhiro
'''
from rest_framework import generics, viewsets
from rest_framework.response import Response
from django.conf import settings
from activities.serializers.daemon_settings_serializer import AudioSettingsSerializer
from activities.modules.client_info import ClientInfo
from bootstrap.bootstrap import get_app_dir
import json
import os
import signal

class DaemonSettingsViewSet(viewsets.GenericViewSet):
    # デーモンプログラムの設定情報を取り扱うクラス。設定情報はデータベースではなく、ファイルに保存される。
    # フロントエンドから設定のアップデート情報を受け取り、ファイルに保存
    # デーモンプログラムからの要求により、設定情報を返す

    serializer_class = AudioSettingsSerializer
    file_path = None

    def get_filename(self, request):
        params = request.query_params
        file_name = "daemon_settings.json"
        if "file" in params:
            if params.get('file').lower() == "audio":
                file_name = "audio_settings.json"
        self.file_path = get_app_dir() / "config" / file_name
        #self.file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    def get_file_object(self):
        # ファイルを読み込みオブジェクトに変換する
        st_obj = None
        try:
            with open(self.file_path, "r") as f:
                st_obj = json.load(f)
        except Exception as e:
            print(e)
        return st_obj

    def set_file_object(self, obj):
        with open(self.file_path, "w") as f:
            json.dump(obj, f, indent=4)
        return True

    def retrieve(self, request, *args, **kwargs):
        # デーモンから設定ファイルの要求と共にプロセスIDが送られて来た場合に、
        # これをシングルトンクラスであるClientInfoに格納する
        params = request.query_params
        if "process_id" in params:
            pid = int(params.get("process_id"))
            #print(pid)
            ClientInfo().setPid(pid)
        # ファイルから情報を取り出す
        self.get_filename(request)
        st_obj = self.get_file_object()
        serializer = self.get_serializer(st_obj)
        return Response(serializer.data)
        

    def update(self, request, *args, **kwargs):
        # 設定情報を変更するときに呼び出されるメソッド
        self.get_filename(request)
        st_obj = self.get_file_object()
        #print(f"->{st_obj}")
        data = request.data
        #print(f"->{data}")
        #print(f"->{data.items()}")
        for item in data.items():
            st_obj[item[0]] = item[1]
            #setattr(st_obj, item[0], item[1])
        # ファイルを書き出す
        self.set_file_object(st_obj)
        serializer = self.get_serializer(st_obj)

        # クライアントにSIGTERMを送り、audioデーモンを再起動する
        # os.kill(ClientInfo().pid, signal.SIGTERM)

        return Response(serializer.data)
        

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class AudioSettings:

    Poll_time = 0.2
    Loop_back_device = "BlackHole"
    Host_api = "Core Audio"
    FORMAT = "pyaudio.paInt16"
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    Silence_threshold = 10
    Start_frame_threshold = 10
    End_frame_threshold = 50
    RETRY_INTERVAL = 50

    def __init__(self):
        pass



