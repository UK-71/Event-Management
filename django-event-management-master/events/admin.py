from django.contrib import admin
from .models import (
    EventCategory,
    Event,
    EventImage,
    EventAgenda,
    EventUserWishList,
    UserCoin,
    Registration,
    Attendance  # ✅ Import Attendance
)

# Optional: Add __str__ methods in Event, Team, TeamMember if needed
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'team', 'member', 'status')  # Display columns
    list_filter = ('event', 'status')                     # Filters on the right
    search_fields = ('event__name', 'team__name', 'member__name')  # Search bar

# Unregister models first (if they are already registered)
if admin.site.is_registered(Event):
    admin.site.unregister(Event)

if admin.site.is_registered(Registration):
    admin.site.unregister(Registration)

# Register models
admin.site.register(EventCategory)
admin.site.register(Event)
admin.site.register(EventImage)
admin.site.register(EventAgenda)
admin.site.register(EventUserWishList)
admin.site.register(UserCoin)
admin.site.register(Registration)
admin.site.register(Attendance, AttendanceAdmin)  # ✅ Register Attendance
