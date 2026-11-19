from django.urls import path
from . import views

app_name = "drive"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("upload/", views.upload_file_view, name="upload"),
    path("view/<int:file_id>/", views.view_file, name="view_file"),
    path("delete/<int:file_id>/", views.delete_file_view, name="delete_file"),
    path("create-folder/", views.create_folder_view, name="create_folder"),
    path("rename-folder/<int:folder_id>/",views.rename_folder_view,name="rename_folder"),
    path("delete-folder/<int:folder_id>/",
    views.delete_folder_view,name="delete_folder"),
    path("folder/<int:folder_id>/",
    views.folder_detail_view,name="folder_detail"),
    path("move/<int:file_id>/", views.move_file_view, name="move_file"),
    path( "download/<int:file_id>/",views.download_file,name="download_file"
),
]