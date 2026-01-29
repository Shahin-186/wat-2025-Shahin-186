from django.core.management.base import BaseCommand
from django.utils import timezone
from supply_chain.models import Project, ProjectSupplier
import random
from datetime import date, timedelta


SAMPLE_LOCATIONS = [
    'North Ward', 'Eastside', 'Central City', 'Riverside', 'Old Town', 'West End', 'Armley', 'Leeds',
    'Greenwich', 'Hillside'
]


def choose_location(p):
    if p.location:
        return p.location
    # prefer council name if present
    if getattr(p.council, 'name', None):
        return p.council.name
    return random.choice(SAMPLE_LOCATIONS)


def generate_description(p):
    title = p.title.lower()
    if 'library' in title or 'library' in getattr(p.title, 'lower', lambda: '')():
        return (
            "A major refurbishment and digital upgrade of the local library to create a modern community hub. "
            "Work includes reconfiguration of public spaces, improved accessibility, new ICT provision, and a flexible events area "
            "to support outreach and learning programmes. The scheme is expected to improve footfall and local services."
        )
    if 'school' in title or 'primary' in title or 'secondary' in title:
        return (
            "Project to upgrade school facilities to meet growing pupil numbers and improve sports and ICT provision. "
            "Works include internal remodelling, new equipment, acoustic and lighting improvements, and accessibility upgrades. "
            "The project will be delivered in close coordination with the school's leadership and local education authority."
        )
    if 'road' in title or 'resurface' in title or 'highway' in title or 'junction' in title:
        return (
            "A targeted highway improvement scheme to replace failing surfacing, repair kerbs, and upgrade drainage. "
            "The work includes temporary traffic management and is scheduled to minimise delays during peak hours."
        )
    if 'buses' in title or 'express' in title or 'fleet' in title or 'tracking' in title:
        return (
            "Transport improvement scheme to enhance bus services — includes feasibility for new express routes, real-time tracking, "
            "and fleet decarbonisation. The project will improve journey times and passenger information."
        )
    if 'park' in title or 'playground' in title or 'wildlife' in title:
        return (
            "Greenspace investment to modernise play equipment, improve accessibility, and create habitats for local wildlife. "
            "Works include soft landscaping, seating, and measures to improve biodiversity and community use."
        )
    if 'wifi' in title or 'digital' in title or 'cost-of-living' in title:
        return (
            "Digital infrastructure project to increase connectivity and support community access to online services. "
            "Includes installation of public Wi‑Fi hotspots, connectivity to community venues, and ongoing support arrangements."
        )
    if 'heritage' in title or 'facade' in title or 'building' in title:
        return (
            "Conservation-led scheme to restore and improve the external fabric of heritage buildings, ensure structural repairs, "
            "and enhance outward-facing features while preserving historic character."
        )
    if 'university' in title or 'research' in title or 'accommodation' in title:
        return (
            "Higher-education related investment to support research excellence and/or student accommodation. "
            "This covers enabling works, internal fit-out, and specialist services tailored to university requirements."
        )
    if 'arts' in title or 'culture' in title or 'festival' in title:
        return (
            "Funding to support arts and cultural activity, including temporary infrastructure for outdoor events, artist commissions, "
            "and small capital grants for grassroots cultural venues."
        )
    # fallback
    return (
        "A local infrastructure project delivering improvements to public services and facilities. "
        "Work is being coordinated with stakeholders and is expected to be completed on schedule."
    )


def choose_budget(p):
    # If a reasonable budget already exists, leave it; otherwise set an estimate
    if p.budget and p.budget > 1000:
        return p.budget
    title = p.title.lower()
    if 'road' in title or 'bridge' in title:
        return random.randint(200000, 1500000)
    if 'school' in title or 'university' in title or 'accommodation' in title:
        return random.randint(250000, 2000000)
    if 'park' in title or 'playground' in title or 'wildlife' in title:
        return random.randint(20000, 250000)
    if 'bus' in title or 'transport' in title or 'fleet' in title:
        return random.randint(50000, 1000000)
    if 'library' in title or 'arts' in title or 'culture' in title:
        return random.randint(20000, 500000)
    # default
    return random.randint(10000, 250000)


class Command(BaseCommand):
    help = 'Populate/enrich project details (description, budget, project_manager, location, end_date) to look more realistic.'

    def handle(self, *args, **options):
        projects = Project.objects.all()
        updated = 0
        for p in projects:
            changed = False

            # description
            if not p.description or len(p.description.split()) < 15:
                p.description = generate_description(p)
                changed = True

            # location
            loc = choose_location(p)
            if not p.location or p.location.strip() == '':
                p.location = loc
                changed = True

            # project manager
            if not p.project_manager:
                p.project_manager = f"{random.choice(['A. Patel','S. Johnson','L. Brown','M. Singh','R. Taylor','J. Smith'])}"
                changed = True

            # budget
            new_budget = choose_budget(p)
            if not p.budget or p.budget < 1000:
                p.budget = new_budget
                changed = True

            # end_date: if null, set to a plausible date within 3-18 months
            if not p.end_date:
                months = random.randint(3, 18)
                p.end_date = date.today() + timedelta(days=30 * months)
                changed = True

            if changed:
                p.save()
                updated += 1
                self.stdout.write(self.style.SUCCESS(f"Updated project id={p.id} title='{p.title}'"))

        self.stdout.write(self.style.SUCCESS(f'Enrichment complete. {updated} projects updated.'))
