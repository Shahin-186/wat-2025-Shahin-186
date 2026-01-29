# Generated data migration: add ContractorRequirement model and seed demo Projects
from django.db import migrations, models
import random


def create_projects_and_requirements(apps, schema_editor):
    Faker = None
    try:
        from faker import Faker as _Faker
        Faker = _Faker
    except Exception:
        # If Faker is not installed in the environment running migrations, fall back to simple data
        Faker = None

    Council = apps.get_model('supply_chain', 'Council')
    Project = apps.get_model('supply_chain', 'Project')
    ContractorRequirement = apps.get_model('supply_chain', 'ContractorRequirement')

    # Ensure there's at least one council to attach projects to
    council, _ = Council.objects.get_or_create(
        name='Example Council',
        defaults={'contact': 'Alice Example', 'contact_email': 'alice@example.com', 'slug': 'example-council'}
    )

    faker = Faker() if Faker else None

    sample_locations = [
        'Leeds, UK', 'Headingley, Leeds', 'Horsforth, Leeds', 'Seacroft, Leeds',
        'Morley, Leeds', 'Beeston, Leeds', 'Otley, Leeds', 'Guiseley, Leeds'
    ]

    name_templates = [
        'A1 Motorway Junction Upgrade',
        'Leeds Ring Road Roundabout Modification',
        'New-Build Housing Phase 3',
        'Riverbank Flood Relief Scheme',
        'East Leeds Road Resurfacing',
        'South Leeds Bridge Replacement',
        'Northern Bypass Drainage Works',
        'City Centre Tram Link Extension',
        'High Street Pavement Renewal',
        'Industrial Park Utilities Upgrade'
    ]

    requirement_choices = [
        'Excavation', 'Traffic Management', 'Road Surfacing', 'Drainage',
        'Line Painting', 'Site Catering', 'Project Management', 'Security',
        'Concrete Works', 'Crane & Lifting', 'Electrical Installation'
    ]

    created = 0
    for i in range(20):
        title = None
        # pick a realistic title, use templates and append a small suffix occasionally
        base = random.choice(name_templates)
        if faker and random.random() < 0.6:
            title = f"{base} — {faker.city()}"
        else:
            title = f"{base} {i+1}"

        description = None
        if faker:
            description = faker.paragraph(nb_sentences=3)
        else:
            description = f"{title}: A construction project focused on civil works and specialist supply chain coordination."

        budget = random.choice([50000, 100000, 250000, 500000, 750000, 1200000])

        location = random.choice(sample_locations)

        proj = Project.objects.create(
            title=title,
            description=description,
            image='https://via.placeholder.com/800x450?text=' + title.replace(' ', '+'),
            budget=budget,
            council=council,
            location=location
        )

        # Create between 4 and 8 requirements per project
        nreq = random.randint(4, 8)
        reqs = random.sample(requirement_choices, k=nreq)
        for r in reqs:
            notes = faker.sentence() if faker else ''
            ContractorRequirement.objects.create(project=proj, name=r, notes=notes)

        created += 1

    # For visibility when running migrations interactively, print a short summary
    try:
        from django.conf import settings
        if settings.DEBUG:
            print(f"[supply_chain] Created {created} demo projects with requirements.")
    except Exception:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('supply_chain', '0005_project_location'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractorRequirement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='requirements', to='supply_chain.project')),
            ],
        ),
        migrations.RunPython(create_projects_and_requirements),
    ]
