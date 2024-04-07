from django.urls import include, path

from . import views

app_name = "darmstadt_termine"
urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register_notification, name="register"),
    path(
        "activate/<idb64>/<token>/",
        views.activate_notification,
        name="activate",
    ),
    path("edit/<token>/", views.edit_notification, name="edit"),
    path("delete/<token>/", views.delete_notification, name="delete"),
    path(
        "delete/<idb64>/<token>/",
        views.delete_notification,
        name="delete",
    ),
    path(
        "reset/",
        include(
            [
                path("", views.reset_notification, name="reset"),
                path(
                    "confirm/<idb64>/<token>/",
                    views.reset_notification_confirm,
                    name="reset_confirm",
                ),
            ]
        ),
    ),
]
