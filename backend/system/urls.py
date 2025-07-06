from django.urls import path
from rest_framework import routers
from .views import DatabaseUploadView, DatabaseInfoView, DBUpdateHistoryViewSet, TableMigrationView, InitDBView
#from .views import DatabaseUploadView, DatabaseInfoView, DatabaseMigrationView, DBUpdateHistoryViewSet, TableMigrationView, InitDBView

router = routers.DefaultRouter()
router.register(r'UpdateHistory', DBUpdateHistoryViewSet)

urlpatterns = [
   path('dbupload/', DatabaseUploadView.as_view(), name='database_upload'),    
   path('dbinfo/', DatabaseInfoView.as_view(), name='database_info'),
   #path('dbmigrate/', DatabaseMigrationView.as_view(), name='database_migration'),
   path('tbmigrate/', TableMigrationView.as_view(), name='table_migration'),
   path('init_db/', InitDBView.as_view(), name='init_db'),
]

urlpatterns += router.urls