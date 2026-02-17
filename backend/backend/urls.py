"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#from django.contrib import admin
from django.urls import path
from django.conf.urls import include


from django.shortcuts import render


#from activities.urls import router as activities_router

from django.conf import settings # New
from django.contrib.staticfiles.urls import static # New
from django.contrib.staticfiles.urls import staticfiles_urlpatterns # New

from django.contrib.auth.decorators import login_required
from django.conf import settings
from activities.decolators import attach_decorator

# reactの画面を呼ぶindex.htmlを表示するビュー
# ログイン画面からリダイレクトされて呼ばれるが、
# ログインされずに呼ばれた場合は表示を行わず、loginHomeに飛ぶ
# index.htmlはfrontend/の下に置かれたものを読み込むよう、
# settings.pyのTEMPLATE のDIRに指定されている。
@attach_decorator(settings.QT_MULTI,login_required(login_url=settings.LOGIN_REDIRECT_URL+"/account/loginHome/")) 
def index_view(request):
    #print(request.headers)
    #print("----------------")
    #print(request.COOKIES)
    #print("----------------")
    #print(request.user)
    #print("----------------")
    return render(request, 'index.html')


if settings.QT_MULTI:
    urlpatterns = [
        #path('admin/', admin.site.urls),
        path('account/', include("account.urls")),
        path('api/', include("activities.urls")),
        path('', index_view, name='index'),
        path('date_graphs', index_view, name='index'),
        path('week_graphs', index_view, name='index'),
        path('month_graphs', index_view, name='index'),
        path('year_graphs', index_view, name='index'),
        path('bar_graphs', index_view, name='index'), 
        path('all_graphs', index_view, name='index'), 
        path('categorize', index_view, name='index'), 
        path('multi_categorize', index_view, name='index'), 
        path('editor', index_view, name='index'), 
        path('audios', index_view, name='index'), 
        path('settings', index_view, name='index'), 
        #path('data_and_files', index_view, name='index'),    
    ]
else:
    urlpatterns = [
        #path('admin/', admin.site.urls),
        path('system/', include("system.urls")),
        path('api/', include("activities.urls")),
        path('', index_view, name='index'),
        path('dashboard', index_view, name='index'),
        path('date_graphs', index_view, name='index'),
        path('week_graphs', index_view, name='index'),
        path('month_graphs', index_view, name='index'),
        path('year_graphs', index_view, name='index'),
        path('bar_graphs', index_view, name='index'), 
        path('all_graphs', index_view, name='index'), 
        path('categorize', index_view, name='index'), 
        path('multi_categorize', index_view, name='index'), 
        path('editor', index_view, name='index'), 
        path('audios', index_view, name='index'), 
        path('settings', index_view, name='index'), 
        path('about_this', index_view, name='index'),
        #path('data_and_files', index_view, name='index'),    
    ]


urlpatterns += staticfiles_urlpatterns() # New
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # New


