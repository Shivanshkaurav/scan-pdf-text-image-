from django.db import models

class Summary(models.Model):
    title = models.CharField(max_length=100)
    summary = models.TextField()
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Summary"
        verbose_name_plural = "Summaries"