from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Your name", "class": ""}),
        label="Name",
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com", "class": ""}),
        label="Email",
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Your message", "rows": 6, "class": ""}),
        label="Message",
    )

    def clean_message(self):
        msg = self.cleaned_data.get("message", "").strip()
        if len(msg) < 5:
            raise forms.ValidationError("Message is too short.")
        return msg


from django.forms import ModelForm
from .models import Supplier


class SupplierForm(ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'contact_email', 'phone', 'address']


from .models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'image', 'category', 'budget', 'council']


from django.forms import ModelForm
from .models import Event


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'location', 'council', 'project', 'image', 'image_file']
