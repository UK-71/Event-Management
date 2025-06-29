from django.db import models
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.utils.timezone import now



class EventCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    id = models.PositiveIntegerField(unique=True, primary_key=True)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_user')
    updated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_user')
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    ACCESS_TYPES = (
        ('our college', 'Our College'),
        ('other college', 'Other College'),
        ('both', 'Both'),
    )
    access_type = models.CharField(choices=ACCESS_TYPES, max_length=25, default='both')  # ✅ Fixed default value

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('event-category-list')


class Team(models.Model):
    name = models.CharField(max_length=255)
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='teams')  # The event the team belongs to
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_created_user')
    updated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_updated_user')
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('team-list')


class Event(models.Model):
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    uid = models.PositiveIntegerField(unique=True)
    description = RichTextUploadingField()
    venue = models.CharField(max_length=255)
    min_team_size = models.IntegerField(default=1)  # New field
    max_team_size = models.IntegerField(default=2)  # New field
    start_date = models.DateField()
    end_date = models.DateField()
    maximum_attendees = models.PositiveIntegerField(default=100)

    created_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='event_created_user')
    updated_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='event_updated_user')
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    STATUS_CHOICES = (
        ('disabled', 'Disabled'),
        ('active', 'Active'),
        ('deleted', 'Deleted'),
        ('time out', 'Time Out'),
        ('completed', 'Completed'),
        ('cancel', 'Cancel'),
    )
    status = models.CharField(choices=STATUS_CHOICES, max_length=10)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('event-list')

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_user:
            self.created_user = self.updated_user  # ✅ Ensuring `created_user` is set properly
        super().save(*args, **kwargs)

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Who is giving feedback
    event = models.ForeignKey('Event', on_delete=models.CASCADE)  # Feedback for which event
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)  # Rating (1 to 5)
    comment = models.TextField(blank=True, null=True)  # User comments
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f'Feedback by {self.user.username} for {self.event.name}'


class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='event_image/')

    def __str__(self):
        return f"Image for {self.event.name}"


class EventAgenda(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    start_time = models.TimeField()


class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    team = models.ForeignKey(Team, on_delete=models.CASCADE,null=True,blank=True)
    event = models.ForeignKey("Event", on_delete=models.CASCADE)
    team_name = models.CharField(max_length=255, default="No Team", null=True, blank=True)  # Default team name
    status = models.CharField(
        max_length=20,
        choices=[("registered", "Registered"), ("canceled", "Canceled")],
        default="registered"  # Default status
    )
    upi_id = models.CharField(max_length=100, default="Unknown", null=True, blank=True)  # Default UPI ID
    team_size = models.IntegerField(default=1, null=True, blank=True)  # Default to single-member team


class TeamMember(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name="team_members")
    name = models.CharField(max_length=255, default="Unknown Member")
    college_name = models.CharField(max_length=255, default="Unknown College")
    email = models.EmailField(default="default@example.com")
    contact_number = models.CharField(max_length=15, default="0000000000")

    def __str__(self):
        return self.name



class Attendance(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.SET_NULL, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=10, choices=[("present", "Present"), ("absent", "Absent")], default="absent")

    def __str__(self):
        return f"{self.event.name} - {self.member.name} ({self.status})"



class AbsenceUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    reason = models.TextField(blank=True, null=True)
    date_reported = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.name}"


class EventUserWishList(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventwishlist_created_user')
    updated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventwishlist_updated_user')
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    STATUS_CHOICES = (
        ('disabled', 'Disabled'),
        ('active', 'Active'),
        ('deleted', 'Deleted'),
        ('blocked', 'Blocked'),
        ('completed', 'Completed'),
    )
    status = models.CharField(choices=STATUS_CHOICES, max_length=10)

    class Meta:
        unique_together = ('event',)  # ✅ Only enforce uniqueness on the event

    def __str__(self):
        return f"{self.event.name} - {self.status}"
    
    def get_absolute_url(self):
        return reverse('event-wish-list')


class UserCoin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    CHOICE_GAIN_TYPE = (
        ('event', 'Event'),
        ('others', 'Others'),
    )
    gain_type = models.CharField(max_length=6, choices=CHOICE_GAIN_TYPE)
    gain_coin = models.PositiveIntegerField()
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usercoin_created_user')
    updated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usercoin_updated_user')
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)

    STATUS_CHOICES = (
        ('disabled', 'Disabled'),
        ('active', 'Active'),
        ('deleted', 'Deleted'),
        ('blocked', 'Blocked'),
        ('completed', 'Completed'),
    )
    status = models.CharField(choices=STATUS_CHOICES, max_length=10)

    def __str__(self):
        return str(self.user)
    
    def get_absolute_url(self):
        return reverse('user-mark')


class EventUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default="participant")  # Role: Participant, Organizer, etc.
    date_joined = models.DateTimeField(auto_now_add=True)  # Timestamp when added

    def __str__(self):
        return f"{self.user.username} - {self.event.name} ({self.role})"
