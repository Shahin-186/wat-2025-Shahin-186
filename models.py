from django.db import models


class Council(models.Model):
    name = models.CharField(max_length=100)

    contact = models.CharField(max_length=100)
    contact_email = models.EmailField()

    slug = models.SlugField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} Council'


class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    # optional image URL (use ImageField if you prefer file uploads and have Pillow installed)
    image = models.URLField(max_length=500, blank=True)
    # primary image for listing views
    main_image = models.URLField(max_length=500, blank=True)

    # optional category relation (Category defined below)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)

    budget = models.IntegerField()

    # main contact for the project
    project_manager = models.CharField(max_length=120, blank=True)

    # optional location string (e.g., "Leeds, UK" or a neighbourhood)
    location = models.CharField(max_length=150, blank=True)

    council = models.ForeignKey(Council, on_delete=models.CASCADE)

    # optional expected end date for the project
    end_date = models.DateField(null=True, blank=True)

    # suppliers attached to the project (through ProjectSupplier)
    suppliers = models.ManyToManyField('Supplier', through='ProjectSupplier', related_name='projects', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title}'


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=150)
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Community(models.Model):
    title = models.CharField(max_length=150)
    link = models.URLField(max_length=500)

    def __str__(self):
        return self.title


class Supplier(models.Model):
    name = models.CharField(max_length=150, unique=True)
    contact_person = models.CharField(max_length=120, blank=True)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.TextField(blank=True)
    specialty = models.CharField(max_length=120, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ContractorRequirement(models.Model):
    """A short descriptor of a contractor requirement for a Project.

    Examples: 'Excavation', 'Traffic Management', 'Road Surfacing'.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='requirements')
    name = models.CharField(max_length=120)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.project.title}"


class ProjectSupplier(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_suppliers')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier_projects')
    contract_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('project', 'supplier'),)

    def __str__(self):
        return f"{self.supplier.name} @ {self.project.title} — £{self.contract_value if self.contract_value else 'n/a'}"


class CouncilMeeting(models.Model):
    """A simple model to store council meetings / events."""
    council = models.ForeignKey(Council, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=250, blank=True)
    agenda = models.TextField(blank=True)
    archived = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        when = self.date.isoformat()
        if self.time:
            when = f"{when} {self.time.strftime('%H:%M')}"
        loc = f" — {self.location}" if self.location else ""
        return f"Meeting: {when}{loc}"


class Event(models.Model):
    """General-purpose events (community events or project milestones).

    An Event can optionally be attached to a Project to represent a project end
    date or milestone. Council is optional and useful for community/council events.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=250, blank=True)
    # optional image URL (can point at /static/ path or external URL)
    image = models.URLField(max_length=500, blank=True)
    # uploaded image file (preferred) stored under MEDIA_ROOT/events/
    image_file = models.ImageField(upload_to='events/', null=True, blank=True)
    council = models.ForeignKey(Council, on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        when = self.date.isoformat()
        if self.time:
            when = f"{when} {self.time.strftime('%H:%M')}"
        return f"Event: {self.title} — {when}"
