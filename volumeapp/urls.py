# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.home),
#     path('video_feed/', views.video_feed),
#     path('start/', views.start_camera),
#     path('stop/', views.stop_camera),
#     path('update/', views.update_settings),
#     path('data/', views.detection_data),
# ]
                                                          # working code
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.index, name='home'),
#     path('start/', views.start_camera),
#     path('stop/', views.stop_camera),
#     path('video_feed/', views.video_feed, name='video_feed'),
#     path('data/', views.detection_data),
# ]

# from django.urls import path
# from . import views



from django.urls import path
from . import views

urlpatterns = [
    path('', views.final_page),
    path('video_feed/', views.video_feed),
    path('gesture-data/', views.get_gesture_data),
    path('start-camera/', views.start_camera),
    path('stop-camera/', views.stop_camera),
    path('capture/', views.capture_frame),
]