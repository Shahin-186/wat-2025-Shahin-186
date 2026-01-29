from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from .models import Council, Project, Supplier, ProjectSupplier, CouncilMeeting, Event
from django.db.models import Prefetch
from .forms import ContactForm, SupplierForm, ProjectForm, EventForm


def hello_world_index(request):
    return HttpResponse("Hello World! This is the main index of the Suppy Chain project")


def home_view(request):
    """Render the home template."""
    # Load a small set of recent projects for the homepage
    projects = Project.objects.select_related('council', 'category').order_by('-created_at')[:4]

    # Upcoming meetings: only non-archived meetings with date >= today
    import datetime

    today = datetime.date.today()
    meetings = (
        CouncilMeeting.objects.filter(archived=False, date__gte=today)
        .select_related('council')
        .order_by('date', 'time')[:4]
    )

    context = {
        'projects': projects,
        'meetings': meetings,
    }

    return render(request, 'supply_chain/home.html', context)


def about_view(request):
    """Render the about template."""
    return render(request, 'supply_chain/about.html')


def service_planning_view(request):
    """Simple landing for Planning & Zoning service."""
    form = ContactForm()
    return render(request, 'supply_chain/services/planning.html', {'form': form})


def service_waste_view(request):
    """Simple landing for Waste & Recycling service."""
    form = ContactForm()
    return render(request, 'supply_chain/services/waste.html', {'form': form})


def service_taxation_view(request):
    """Simple landing for Taxation & Rates service."""
    form = ContactForm()
    return render(request, 'supply_chain/services/taxation.html', {'form': form})


def service_licenses_view(request):
    """Simple landing for Licenses & Permits service."""
    form = ContactForm()
    return render(request, 'supply_chain/services/licenses.html', {'form': form})


def service_request_view(request):
    """Handle a simple service enquiry using the existing ContactForm.

    The form should include a hidden `service` field indicating which service the user
    is enquiring about. On success we redirect to the existing contact_success page.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        service_name = request.POST.get('service', '')
        if form.is_valid():
            # For now we don't persist messages; in a real app we'd save or send an email.
            # Enhance the message with service context for the operator.
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            message = form.cleaned_data.get('message')
            # Combine into a single message (could be emailed or stored)
            combined = f"Service: {service_name}\nFrom: {name} <{email}>\n\n{message}"
            # Log to console for dev visibility
            try:
                import logging

                logger = logging.getLogger(__name__)
                logger.info('Service request submitted: %s', combined)
            except Exception:
                pass

            return redirect('contact_success')
    else:
        # Show a small contact form prefilled with a service field.
        initial = {}
        if 'service' in request.GET:
            initial['message'] = f"Enquiry about service: {request.GET.get('service')}\n\n"
        form = ContactForm(initial=initial)

    return render(request, 'supply_chain/service_request_form.html', {'form': form})


def all_councils(request):
    councils = Council.objects.all()

    context = {
        'councils': councils,
    }

    return render(request, 'supply_chain/all_councils_list.html', context)


def project_detail(request, id):
    project = get_object_or_404(Project.objects.select_related('council'), pk=id)

    context = {
        'project': project,
    }

    return render(request, 'supply_chain/project_detail.html', context)


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # For now we just redirect to a success page. In a real app
            # you might send an email or persist the message.
            return redirect('contact_success')
    else:
        form = ContactForm()

    return render(request, 'supply_chain/contact.html', {'form': form})


def contact_success(request):
    return render(request, 'supply_chain/contact_success.html')


def calendar_view(request):
    """Display a simple calendar-like list of Events and CouncilMeetings.

    For now this shows Events (community & project milestones) and upcoming
    CouncilMeetings ordered by date.
    """
    import datetime

    today = datetime.date.today()
    events = Event.objects.filter(date__gte=today).select_related('council', 'project').order_by('date', 'time')
    meetings = CouncilMeeting.objects.filter(archived=False, date__gte=today).select_related('council').order_by('date', 'time')

    context = {
        'events': events,
        'meetings': meetings,
    }
    return render(request, 'supply_chain/calendar.html', context)


def event_create_view(request):
    """Simple form to create an Event. If a Project is selected, and the event
    looks like a project end milestone, we also set the project's `end_date`.
    """
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            ev = form.save()
            # If linked to a project, optionally set its end_date to the event date
            if ev.project:
                ev.project.end_date = ev.date
                ev.project.save()
            messages.success(request, 'Event created successfully.')
            return redirect('calendar')
    else:
        form = EventForm()

    return render(request, 'supply_chain/event_form.html', {'form': form})


def event_detail_view(request, pk):
    from django.shortcuts import get_object_or_404
    ev = get_object_or_404(Event, pk=pk)
    return render(request, 'supply_chain/event_detail.html', {'event': ev})


def meeting_detail_view(request, pk):
    from django.shortcuts import get_object_or_404
    meeting = get_object_or_404(CouncilMeeting, pk=pk)
    return render(request, 'supply_chain/meeting_detail.html', {'meeting': meeting})


def cost_of_living_view(request):
    """Render the cost of living guidance page."""
    # Load local CSV data for average rents and supermarket index
    import csv
    from pathlib import Path

    data_file = Path(__file__).resolve().parent / 'data' / 'cost_of_living_rents.csv'
    areas = []
    try:
        with open(data_file, newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                # coerce numeric fields
                try:
                    row['avg_rent_1br_gbp'] = int(row.get('avg_rent_1br_gbp') or 0)
                except Exception:
                    row['avg_rent_1br_gbp'] = 0
                try:
                    row['avg_rent_2br_gbp'] = int(row.get('avg_rent_2br_gbp') or 0)
                except Exception:
                    row['avg_rent_2br_gbp'] = 0
                try:
                    row['supermarket_index'] = float(row.get('supermarket_index') or 1.0)
                except Exception:
                    row['supermarket_index'] = 1.0
                areas.append(row)
    except FileNotFoundError:
        areas = []

    return render(request, 'supply_chain/cost_of_living.html', {'areas': areas})


# Supplier CRUD (class-based views)
class SupplierListView(generic.ListView):
    model = Supplier
    template_name = 'supply_chain/suppliers/supplier_list.html'
    context_object_name = 'suppliers'


class SupplierDetailView(generic.DetailView):
    model = Supplier
    template_name = 'supply_chain/suppliers/supplier_detail.html'


class SupplierCreateView(SuccessMessageMixin, generic.CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'supply_chain/suppliers/supplier_form.html'
    success_url = reverse_lazy('supplier-list')
    success_message = "Supplier '%(name)s' was created successfully."


class SupplierUpdateView(SuccessMessageMixin, generic.UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'supply_chain/suppliers/supplier_form.html'
    success_url = reverse_lazy('supplier-list')
    success_message = "Supplier '%(name)s' was updated successfully."


class SupplierDeleteView(generic.DeleteView):
    model = Supplier
    template_name = 'supply_chain/suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier-list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Supplier '{obj.name}' was deleted.")
        return super().delete(request, *args, **kwargs)


# Project CRUD (class-based views)
class ProjectListView(generic.ListView):
    model = Project
    template_name = 'supply_chain/projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20

    def get_queryset(self):
        from django.db import models as dj_models
        from django.utils.dateparse import parse_date

        qs = Project.objects.select_related('council', 'category').order_by('-created_at')

        # text search
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                dj_models.Q(title__icontains=q)
                | dj_models.Q(description__icontains=q)
                | dj_models.Q(location__icontains=q)
                | dj_models.Q(category__name__icontains=q)
            )

        # budget filters
        min_budget = self.request.GET.get('min_budget')
        max_budget = self.request.GET.get('max_budget')
        try:
            if min_budget:
                qs = qs.filter(budget__gte=int(min_budget))
        except (ValueError, TypeError):
            pass
        try:
            if max_budget:
                qs = qs.filter(budget__lte=int(max_budget))
        except (ValueError, TypeError):
            pass

        # created_at date range filters (dates in YYYY-MM-DD)
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        try:
            if start_date:
                sd = parse_date(start_date)
                if sd:
                    qs = qs.filter(created_at__date__gte=sd)
        except Exception:
            pass
        try:
            if end_date:
                ed = parse_date(end_date)
                if ed:
                    qs = qs.filter(created_at__date__lte=ed)
        except Exception:
            pass

        return qs


class ProjectDetailView(generic.DetailView):
    model = Project
    template_name = 'supply_chain/projects/project_detail.html'

    def get_queryset(self):
        # Select related fields for the project itself, and prefetch related
        # ProjectSupplier rows with their supplier to avoid N+1 queries.
        ps_qs = ProjectSupplier.objects.select_related('supplier')
        return (
            super()
            .get_queryset()
            .select_related('council', 'category')
            .prefetch_related(Prefetch('project_suppliers', queryset=ps_qs))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # The project instance is available as `self.object` (or context['object']).
        # Use the prefetched related name `project_suppliers` to access the link rows.
        project = self.object
        project_suppliers = getattr(project, 'project_suppliers', None)
        # Ensure we pass an iterable (QuerySet) to the template (may be None for empty)
        context['project_suppliers'] = project_suppliers.all() if project_suppliers is not None else []
        return context


class ProjectCreateView(SuccessMessageMixin, generic.CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'supply_chain/projects/project_form.html'
    success_url = reverse_lazy('projects-list')
    success_message = "Project '%(title)s' was created successfully."


class ProjectUpdateView(SuccessMessageMixin, generic.UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'supply_chain/projects/project_form.html'
    success_url = reverse_lazy('projects-list')
    success_message = "Project '%(title)s' was updated successfully."


class ProjectDeleteView(generic.DeleteView):
    model = Project
    template_name = 'supply_chain/projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects-list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Project '{obj.title}' was deleted.")
        return super().delete(request, *args, **kwargs)

