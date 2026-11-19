from django.db import models
from django.contrib.auth.models import User
import os


def user_upload_path(instance, filename):
    return f"user_{instance.user.id}/{filename}"


class DriveFolder(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="drive_folders"
    )

    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_folder_name_per_user"
            )
        ]

    def __str__(self):
        return self.name


class DriveFile(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="drive_files"
    )

    folder = models.ForeignKey(
        DriveFolder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="files"
    )

    file = models.FileField(upload_to=user_upload_path)

    original_name = models.CharField(max_length=255)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_name

    @property
    def file_size(self):
        if self.file and self.file.storage.exists(self.file.name):
            return self.file.size
        return 0

    @property
    def extension(self):
        return os.path.splitext(self.original_name)[1].lower()