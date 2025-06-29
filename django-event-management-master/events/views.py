from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    DeleteView,
    View,
)
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import (
    EventCategory,
    Event,
    Registration,
    EventUserWishList,
    UserCoin,
    EventImage,
    EventAgenda,
)
from .forms import EventForm, EventImageForm, EventAgendaForm, EventCreateMultiForm

from .models import Event
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    return render(request, "events/profile.html") 

def home(request):
    events = Event.objects.all()  # Fetch events
    return render(request, 'base/sidebar.html', {'events': events})
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Attendance, AbsenceUser, Event, TeamMember, Registration
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def attendance_list(request):
    # Fetch events the user has registered for
    registered_events = Registration.objects.filter(user=request.user).select_related('event')

    # Get all event IDs
    event_ids = registered_events.values_list('event_id', flat=True)

    # Get attendance records for those events
    attendance_records = Attendance.objects.filter(event_id__in=event_ids)
    
    # Build attendance data
    attendances = []
    for reg in registered_events:
        event = reg.event
        attendance = attendance_records.filter(event=event).first()  # Get first attendance record
        
        # Get all team members for this registration
        team_members = TeamMember.objects.filter(registration=reg)
        
        for member in team_members:
            attendances.append({
                "event_id": event.id,
                "event_name": event.name,
                "team_name": reg.team_name,
                "upi_id": reg.upi_id,
                "team_size": reg.team_size,
                "member_name": member.name,
                "email": member.email,
                "contact_number": member.contact_number,
                "attendance": attendance.get_status_display() if attendance else "Not Marked",
                "attendance_id": attendance.id if attendance else None
            })

    # Handle AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"attendances": attendances}, safe=False)

    return render(request, 'events/attendance_list.html', {"events": registered_events})


def registration_success(request):
    return render(request, 'events/registration_success.html')  # Ensure this template exists

@login_required
def mark_attendance(request):
    if request.method == "POST":
        member_id = request.POST.get("member_id")
        event_id = request.POST.get("event_id")
        attendance_status = request.POST.get("attendance_status")

        try:
            member = TeamMember.objects.get(id=member_id)
            event = Event.objects.get(id=event_id)

            attendance, created = Attendance.objects.get_or_create(
                member=member, event=event, defaults={"status": attendance_status}
            )
            if not created:
                attendance.status = attendance_status
                attendance.save()

        except TeamMember.DoesNotExist:
            messages.error(request, "Member not found!")
        except Event.DoesNotExist:
            messages.error(request, "Event not found!")

    return redirect("attendance_list")

@csrf_exempt
def save_attendance(request):
    if request.method == "POST":
        data = json.loads(request.body)
        attendance_id = data.get("attendance_id")
        status = data.get("status")

        try:
            attendance = Attendance.objects.get(id=attendance_id)
            attendance.attendance = status
            attendance.save()

            # If Absent, add to AbsenceUser
            if status == "Absent":
                AbsenceUser.objects.create(
                    member_name=attendance.member_name,
                    email=attendance.email,
                    contact_number=attendance.contact_number,
                    event=attendance.event
                )

            return JsonResponse({"success": True})
        except Attendance.DoesNotExist:
            return JsonResponse({"success": False, "error": "Attendance record not found"})

    return JsonResponse({"success": False, "error": "Invalid request"})

@csrf_exempt
def save_absence(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            event_id = data.get("event_id")
            name = data.get("name")
            email = data.get("email")
            contact_number = data.get("contact_number")

            event = Event.objects.get(id=event_id)

            AbsenceUser.objects.create(
                event=event,
                name=name,
                email=email,
                contact_number=contact_number
            )

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})

# ✅ Added Missing AbsenceUserList Class
class AbsenceUserList(LoginRequiredMixin, ListView):
    """ List users who have been marked absent for events """
    login_url = 'login'
    model = Registration  # Using Registration model to track event attendance
    template_name = 'events/absence_user_list.html'
    context_object_name = 'absent_users'

    def get_queryset(self):
        """Filter registrations where status is 'absent'"""
        return Registration.objects.filter(status="absent")  # Modify as per your logic

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Feedback
from .forms import FeedbackForm

@login_required
def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            return redirect('feedback_success')  # Redirect to a success page
    else:
        form = FeedbackForm()
    
    return render(request, 'events/feedback.html', {'form': form})

def feedback_success(request):
    return render(request, 'events/feedback_success.html')

# Event category list view
class EventCategoryListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = EventCategory
    template_name = 'events/event_category.html'
    context_object_name = 'event_category'


class EventCategoryCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = EventCategory
    fields = ['name', 'id', 'access_type']
    template_name = 'events/create_event_category.html'

    def form_valid(self, form):
        form.instance.created_user = self.request.user
        form.instance.updated_user = self.request.user
        return super().form_valid(form)


class EventCategoryUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = EventCategory
    fields = ['name', 'id', 'access_type']
    template_name = 'events/edit_event_category.html'


class EventCategoryDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = EventCategory
    template_name = 'events/event_category_delete.html'
    success_url = reverse_lazy('event-category-list')


@login_required(login_url='login')
def create_event(request):
    event_form = EventForm()
    event_image_form = EventImageForm()
    event_agenda_form = EventAgendaForm()
    catg = EventCategory.objects.all()

    if request.method == 'POST':
        event_form = EventForm(request.POST)
        event_image_form = EventImageForm(request.POST, request.FILES)
        event_agenda_form = EventAgendaForm(request.POST)

        if event_form.is_valid() and event_image_form.is_valid() and event_agenda_form.is_valid():
            ef = event_form.save()
            event_image = event_image_form.save(commit=False)
            event_image.event = ef
            event_image.save()

            event_agenda = event_agenda_form.save(commit=False)
            event_agenda.event = ef
            event_agenda.save()

            return redirect('event-list')
        if form.is_valid():
            event = form.save(commit=False)
            event.min_team_size = form.cleaned_data['min_team_size']
            event.max_team_size = form.cleaned_data['max_team_size']
            event.save()
    context = {
        'form': event_form,
        'form_1': event_image_form,
        'form_2': event_agenda_form,
        'ctg': catg
    }
    return render(request, 'events/create.html', context)
    


class EventCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    form_class = EventCreateMultiForm
    template_name = 'events/create_event.html'
    success_url = reverse_lazy('event-list')

    def form_valid(self, form):
        evt = form['event'].save()
        event_image = form['event_image'].save(commit=False)
        event_image.event = evt
        event_image.save()

        event_agenda = form['event_agenda'].save(commit=False)
        event_agenda.event = evt
        event_agenda.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ctg'] = EventCategory.objects.all()
        return context

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Event, Registration, TeamMember

@login_required
def register_event(request):
    if request.method == "POST":
        event_id = request.POST.get("event")
        event = get_object_or_404(Event, id=event_id)

        # Check if the user has already registered for the event
        existing_registration = Registration.objects.filter(event=event, user=request.user).exists()
        if existing_registration:
            messages.warning(request, "You have already registered for this event.")
            events = Event.objects.filter(status="active")
            return render(request, "events/register_event.html", {"events": events})

        # Create the Registration entry
        registration = Registration.objects.create(
            user=request.user,
            event=event,
            team_name=request.POST.get("team_name"),
            upi_id=request.POST.get("upi_id"),
            team_size=request.POST.get("team_size"),
            status="registered"
        )

        # Save team members
        team_size = int(request.POST.get("team_size", 1))  # Default to 1 if missing
        for i in range(1, team_size + 1):
            TeamMember.objects.create(
                registration=registration,
                name=request.POST.get(f"member_{i}_name"),
                college_name=request.POST.get(f"member_{i}_college"),
                email=request.POST.get(f"member_{i}_email"),
                contact_number=request.POST.get(f"member_{i}_phone"),
            )

        messages.success(request, "Successfully registered for the event.")
        return redirect("my-events")

    events = Event.objects.filter(status="active")  # Show only active events
    return render(request, "events/register_event.html", {"events": events})



from django.shortcuts import render
from .models import Registration, TeamMember
@login_required
def my_events(request):
    registered_events = Registration.objects.filter(user=request.user).select_related('event')

    # Debugging: Print registered events
    print(f"📝 My Events for {request.user}: {[reg.event.name for reg in registered_events]}")

    return render(request, "events/my_events.html", {"registered_events": registered_events})

def registration_success(request):
    return render(request, 'events/registration_success.html')  # Ensure this template exists

@login_required
def cancel_registration(request):
    if request.method == "POST":
        registration_id = request.POST.get("registration_id")
        print(f"🔍 Received registration ID: {registration_id}")  # Debugging

        if not registration_id:
            print("❌ No registration ID received!")
            messages.error(request, "Invalid request. No registration ID provided.")
            return redirect("my-events")

        # 🔥 FIX: Use user instead of email
        registration = get_object_or_404(Registration, id=registration_id, user=request.user)

        print(f"🗑️ Deleting registration for {registration.event.name}")
        registration.delete()

        messages.success(request, f"Successfully removed {registration.event.name} from your events.")
        return redirect("my-events")

    # 🔥 FIX: Use user instead of email
    registered_events = Registration.objects.filter(user=request.user)

    return render(request, "events/cancel_registration.html", {"registered_events": registered_events})

class AbsenceUserList(LoginRequiredMixin, ListView):
    """ List users who have been marked absent for events """
    login_url = 'login'
    model = Registration  # Ensure this model tracks attendance
    template_name = 'events/absence_user_list.html'
    context_object_name = 'absenceuser'  # Match this with the template variable name

    def get_queryset(self):
        """Filter registrations where status is 'absent'"""
        return Registration.objects.filter(status="absent")  # Make sure "absent" exists in DB


from .models import EventUser  # Ensure this model exists

class CompleteEventUserList(ListView):
    model = EventUser
    template_name = "events/complete_event_user_list.html"
    context_object_name = "event_users"

class EventListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'


class EventUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Event
    fields = ['category', 'name', 'uid', 'description', 'venue','min_team_size', 'max_team_size', 'start_date', 'end_date', 'maximum_attendees', 'status']
    template_name = 'events/edit_event.html'


class EventDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'


class EventDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Event
    template_name = 'events/delete_event.html'
    success_url = reverse_lazy('event-list')


class EventUserWishListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = EventUserWishList
    template_name = 'events/event_user_wish_list.html'
    context_object_name = 'eventwish'


class AddEventUserWishListCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = EventUserWishList
    fields = ['event', 'status']
    template_name = 'events/add_event_user_wish.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['event'].queryset = Event.objects.filter(status="active")  # ✅ Show only active events
        return form

    def form_valid(self, form):
        form.instance.created_user = self.request.user
        form.instance.updated_user = self.request.user
        return super().form_valid(form)


class RemoveEventUserWishDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = EventUserWishList
    template_name = 'events/remove_event_user_wish.html'
    success_url = reverse_lazy('event-wish-list')


class UpdateEventStatusView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Event
    fields = ['status']
    template_name = 'events/update_event_status.html'


class CompleteEventList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Event
    template_name = 'events/complete_event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(status='completed')


class CreateUserMark(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = UserCoin
    fields = ['user', 'gain_type', 'gain_coin', 'status']
    template_name = 'events/create_user_mark.html'

    def form_valid(self, form):
        form.instance.created_user = self.request.user
        form.instance.updated_user = self.request.user
        return super().form_valid(form)


class UserMarkList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = UserCoin
    template_name = 'events/user_mark_list.html'
    context_object_name = 'usermark'


@login_required(login_url='login')
def search_event_category(request):
    if request.method == 'POST':
        data = request.POST['search']
        event_category = EventCategory.objects.filter(name__icontains=data)
        return render(request, 'events/event_category.html', {'event_category': event_category})
    return render(request, 'events/event_category.html')


@login_required(login_url='login')
def search_event(request):
    if request.method == 'POST':
        data = request.POST['search']
        events = Event.objects.filter(name__icontains=data)
        return render(request, 'events/event_list.html', {'events': events})
    return render(request, 'events/event_list.html')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Event, Registration, Attendance, Team, TeamMember
def mark_attendance(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        for registration in Registration.objects.filter(event=event, status='registered'):
            team = registration.team
            for member in registration.team_members.all():  # ✅ correct relation
                attendance_status = request.POST.get(f'attendance_{member.id}')
                if attendance_status:
                    Attendance.objects.create(
                        registration=registration,
                        event=event,
                        team=team,
                        member=member,
                        status=attendance_status
                    )

        event.status = 'completed'
        event.save()
        return redirect('event-detail', pk=event.id)

    registrations = Registration.objects.filter(event=event, status='registered')
    return render(request, 'events/mark_attendance.html', {
        'event': event,
        'registrations': registrations
    })





# View to list all events with attendance
def attendance_list(request):
    events = Event.objects.all()
    return render(request, 'events/attendance_list.html', {'events': events})


# Detailed event view with attendance per team member
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    registrations = Registration.objects.filter(event=event).select_related('team').prefetch_related('team__teammember_set')
    

    # Lookup {(team_id, member_id): attendance_status}
    attendance_lookup = {
        record.member_id: record.status.capitalize()
        for record in Attendance.objects.filter(event=event)
    }

    for attendance in Attendance.objects.all():
        attendance_lookup[attendance.member.id] = attendance.status

    context = {
    'registrations': registrations,
    'attendance_lookup': attendance_lookup,
}


    return render(request, 'events/event_detail.html', {
        'event': event,
        'registrations': registrations,
        'attendance_lookup': attendance_lookup,
    })


# View to show teams and members registered for an event
def event_teams(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registrations = Registration.objects.filter(event=event, status='registered')

    teams = []
    for registration in registrations:
        team = registration.team
        members = team.teammember_set.all() if team else []
        teams.append({
            'team_name': team.name if team else 'No Team',
            'team_size': len(members),
            'members': members,
        })

    return render(request, 'events/teams_list.html', {'event': event, 'teams': teams})


# Logged-in user’s related events
@login_required
def my_events(request):
    registrations = Registration.objects.filter(user=request.user).select_related('event', 'team').prefetch_related('team__teammember_set')

    # Create a combined attendance_lookup for all events the user is registered for
    event_ids = registrations.values_list('event_id', flat=True)
    attendance_lookup = {
        attendance.member_id: attendance.status.capitalize()
        for attendance in Attendance.objects.filter(event_id__in=event_ids)
    }

    return render(request, 'events/my_events.html', {
        'registrations': registrations,
        'attendance_lookup': attendance_lookup,
    })





# Optional: Class-based DetailView for event (less detailed than the custom one)
from django.views.generic.detail import DetailView

class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        context['registrations'] = event.registration_set.select_related('team').prefetch_related('team__teammember_set')
        context['attendance_lookup'] = {
    a.member.id: a.status.capitalize()
    for a in Attendance.objects.filter(event=event).select_related('member')
}


        return context
    
