import uuid
from django.db import models
from cloudinary.models import CloudinaryField

class Image(models.Model):
    attachment_key = models.UUIDField(
        max_length=255,
        default=uuid.uuid4,
        unique=True,
        help_text=("Used to attach the image to another object. Cannot be used to retrieve the image file."),
    )
    public_id = models.CharField(
        max_length=255,
        unique=True,
        help_text=(
            "Used to retrieve the image itself. Should not be readable until the image is attached to another object."
        ),
    )
    file = CloudinaryField('file')  
    folder = models.CharField(max_length=255, default='media/images')
    description = models.TextField(null=True, blank=True)
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.public_id:  
          
            self.public_id = self.file.public_id  
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description or f"Image {self.id}"

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
        
