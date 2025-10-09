from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from activities.models import ActivityPredictor
from activities.serializer import ActivityPredictorSerializer
from activities.modules.ai.predictor_manager import PredictorManager


# Predictorリストの取得
class ActivityPredictorsView(generics.ListAPIView):
    queryset = ActivityPredictor.objects.all()
    serializer_class = ActivityPredictorSerializer

    def get_queryset(self):
        pid = self.request.query_params.get('p_id')
        if pid is not None:
            queryset = self.queryset.filter(p_id=pid).order_by('created_dtime').reverse()
        return queryset

# Predictorの学習済みモデルを生成
class CreateActivityPredictorView(generics.CreateAPIView):
    serializer_class = ActivityPredictorSerializer
    start = None
    end = None
    data_source ="Activity"
    p_id = None

    def create(self, request, *args, **kwargs):
        self.evaluate_params()
        pi = PredictorManager().create_predictor(self.p_id, start=self.start, end=self.end, data_source=self.data_source)
        serializer = self.get_serializer(pi)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def evaluate_params(self):
        params = self.request.query_params
        print(params)
        if 'start' in params:
            self.start = params.get('start')
        if 'end' in params:
            self.end = params.get('end')
        if 'p_id' in params:
            self.p_id = int(params.get('p_id'))
        if 'data_source' in params:
            self.data_source = params.get('data_source')

#学習済みモデルの削除。削除後にモデルのリストを返す。
class DestroyActivityPredictorView(generics.DestroyAPIView):
    queryset = ActivityPredictor.objects.all()
    serializer_class = ActivityPredictorSerializer

    def destroy(self, request, *args, **kwargs):
        params = self.request.query_params
        if 'p_id' in params:
            self.p_id = int(params.get('p_id'))

        instance = self.get_object()
        print(instance)
        print(instance.p_id)
        print(instance.name)
        result = PredictorManager().delete_predictor(self.p_id, instance.name)
        if result:
            self.perform_destroy(instance)
            queryset = ActivityPredictor.objects.filter(p_id = self.p_id).order_by('created_dtime').reverse()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_423_LOCKED)
    
#パースペクティブに対応する学習済みモデルを起動する。起動後モデルのリストを返す。
class ActivatePredictorView(generics.UpdateAPIView):
    p_id = None
    queryset = ActivityPredictor.objects.all()
    serializer_class = ActivityPredictorSerializer

    def update(self, request, *args, **kwargs):
        params = self.request.query_params
        if 'p_id' in params:
            self.p_id = int(params.get('p_id'))

        # 指定されたモデルの情報から実際の学習モデルのインスタンスを起動する
        new_instance = self.get_object()
        PredictorManager().activate_predictor(new_instance.p_id, new_instance.name)

        #データベースの情報を更新
        # これまでアクティブになっていたモデルがあれば、ノンアクティブに変更
        active_instances = ActivityPredictor.objects.filter(p_id=new_instance.p_id, using=True)
        for i in active_instances:
            i.using = False
            i.save()

        #新たに指定されたモデルをアクティブに変更
        new_instance.using = True
        new_instance.save()

        #queryset = self.filter_queryset(self.get_queryset())
        queryset = ActivityPredictor.objects.filter(p_id = self.p_id).order_by('created_dtime').reverse()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



