from django.db import models


class HoneypotFile(models.Model):
    """Decoy file registry for deception-based ransomware detection."""

    file_path = models.CharField(max_length=512, unique=True)
    is_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.file_path
