from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.db import models

# Create your models here.


class CallerUserManager(UserManager):
    def create_superuser(
        self, username=None, email=None, password=None, **extra_fields
    ):
        name = extra_fields.get("name")
        phone_number = extra_fields.get("phone_number")
        User.objects.create(
            phone_number=phone_number,
            name=name,
            email=email,
            password=make_password(password),
        )


class User(AbstractUser):
    email = models.EmailField(null=True)
    username = models.CharField(max_length=150, null=True)
    phone_number = models.PositiveBigIntegerField(
        unique=True, help_text="unique number for a user to register"
    )
    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["name"]

    objects = CallerUserManager()

    def __str__(self):
        return f"User-{self.name}"


class Contact(models.Model):
    EDUCATION = "Education"
    ENTERTAINMENT_AND_ARTS = "Entertainment & Arts"
    FINANCE_AND_INSURANCE = "Finance & Insurance"
    HEALTH_AND_WELLNESS = "Health & Wellness"

    TAGS = (
        (EDUCATION, "Education"),
        (ENTERTAINMENT_AND_ARTS, "Entertainment and arts"),
        (HEALTH_AND_WELLNESS, "Health and wellness"),
        (FINANCE_AND_INSURANCE, "Finance and insurance"),
    )
    name = models.CharField(max_length=100, help_text="Name of the contact person")
    # username = models.CharField(max_length=100)
    number = models.PositiveBigIntegerField()
    email = models.EmailField(null=True, blank=True)

    is_spam = models.BooleanField(default=False)

    tag = models.CharField(max_length=100, null=True, blank=True, choices=TAGS)

    def __str__(self):
        return f"Contact {self.name}"

    @property
    def is_registered(self):
        return UserProfile.objects.filter(phone_number=self.number).exists()


class UserContact(models.Model):
    """Map user with contact"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_contacts"
    )
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name="user_contacts"
    )

    class Meta:
        unique_together = ("user", "contact")

    def __str__(self):
        return f"user_contact-{self.id}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.PositiveBigIntegerField(unique=True)
    email = models.EmailField(null=True, blank=True)
    name = models.CharField(max_length=100)
    is_spam = models.BooleanField(default=False)

    def __str__(self):
        return f"UserProfile {self.user.name}"
