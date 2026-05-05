from django.contrib import admin
from django.urls import include, path, re_path

import xadmin
xadmin.autodiscover()

from xadmin.plugins import xversion
xversion.register_models()

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^xadmin/', include(xadmin.site.urls)),
]