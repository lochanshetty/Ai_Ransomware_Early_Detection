from django.db import models


class ProtectedFile(models.Model):
    """Registry of sensitive files selected for active monitoring."""

    file_path = models.CharField(max_length=512, unique=True)
    file_type = models.CharField(max_length=16)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.file_path
