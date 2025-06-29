from django import forms
from betterforms.multiform import MultiModelForm
from django.forms import modelformset_factory
from .models import Event, EventImage, EventAgenda
from .models import Registration

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['category', 'name', 'uid', 'description', 'venue','min_team_size', 'max_team_size', 'start_date', 'end_date', 'maximum_attendees', 'status']
        
        widgets = {
            'start_date': forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['venue'].widget.attrs.update({'class': 'form-control'})
        self.fields['maximum_attendees'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})


# Formset for multiple event entries
EventFormSet = modelformset_factory(Event, form=EventForm, extra=3)


from django import forms
from .models import Event, Registration

class EventRegistrationForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=Event.objects.all(), label="Select Event"
    )
    team_name = forms.CharField(max_length=100, label="Team Name")
    status = forms.CharField(max_length=50, label="Ststus")
    upi_id = forms.CharField(max_length=50, label="UPI ID")
    team_size = forms.IntegerField(label="Team Size", min_value=1)

    def __init__(self, *args, **kwargs):
        team_size = kwargs.pop('team_size', 1)  # Default to 1 member if not set
        super().__init__(*args, **kwargs)

        for i in range(1, team_size + 1):
            self.fields[f"member_{i}_name"] = forms.CharField(
                max_length=100, label=f"Member {i} Name"
            )
            self.fields[f"member_{i}_college"] = forms.CharField(
                max_length=100, label=f"Member {i} College Name"
            )
            self.fields[f"member_{i}_email"] = forms.EmailField(
                label=f"Member {i} Email"
            )
            self.fields[f"member_{i}_phone"] = forms.CharField(
                max_length=15, label=f"Member {i} Phone Number"
            )

from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['event', 'rating', 'comment']

class EventImageForm(forms.ModelForm):
    class Meta:
        model = EventImage
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({'class': 'form-control'})


class EventAgendaForm(forms.ModelForm):
    class Meta:
        model = EventAgenda
        fields = ['start_time']

        widgets = {
            'start_time': forms.TextInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_time'].widget.attrs.update({'class': 'form-control'})


class EventCreateMultiForm(MultiModelForm):
    form_classes = {
        'event': EventForm,
        'event_image': EventImageForm,
        'event_agenda': EventAgendaForm,
    }
