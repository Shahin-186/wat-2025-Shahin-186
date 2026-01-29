from django.core.management.base import BaseCommand
from django.db import transaction
import random

try:
    from faker import Faker
except Exception:
    Faker = None

class Command(BaseCommand):
    help = 'Seed the database with suppliers, projects and project-supplier links for development'

    def handle(self, *args, **options):
        faker = Faker() if Faker else None

        from supply_chain.models import Supplier, Project, ProjectSupplier, Council
        with transaction.atomic():
            self.stdout.write('Seeding suppliers...')
            suppliers = []
            specialties = ['Heavy Machinery Rental', 'Aggregates', 'Road Paint', 'Traffic Management', 'Drainage', 'Catering', 'Temporary Fencing', 'Concrete Supplier', 'Plant Hire', 'Groundworks', 'Scaffolding', 'Electrical Supplies', 'Landscaping', 'Surveying']
            # create more suppliers (30) for broader data
            for i in range(30):
                name = faker.company() if faker else f'Supplier {i+1}'
                contact = faker.name() if faker else ''
                phone = faker.phone_number() if faker else ''
                specialty = random.choice(specialties)
                s, created = Supplier.objects.get_or_create(
                    name=name,
                    defaults={
                        'contact_person': contact,
                        'phone': phone,
                        'specialty': specialty,
                    }
                )
                suppliers.append(s)
            self.stdout.write(self.style.SUCCESS(f'Created/Loaded {len(suppliers)} suppliers'))

            # Create multiple councils
            council_names = [
                'Seed Council', 'Northfield Council', 'Southvale Council', 'Riverside Borough',
                'Lakeside Council', 'Hillside District', 'Elmbridge Council', 'Greenwich Council'
            ]
            councils = []
            for idx, cname in enumerate(council_names):
                slug = cname.lower().replace(' ', '-')
                c, created = Council.objects.get_or_create(
                    name=cname,
                    defaults={'contact': f'{cname} Admin', 'contact_email': f'admin+{idx}@example.com', 'slug': slug}
                )
                councils.append(c)

            self.stdout.write('Seeding projects...')
            project_titles = [
                'A1 Motorway Junction Upgrade',
                'Leeds Ring Road Roundabout Modification',
                'New-Build Housing Phase 3',
                'Riverbank Flood Relief Scheme',
                'East Leeds Road Resurfacing',
                'South Leeds Bridge Replacement',
                'Northern Bypass Drainage Works',
                'City Centre Tram Link Extension',
                'High Street Pavement Renewal',
                'Industrial Park Utilities Upgrade',
                'Armley Road Redevelopment',
                'Kirkstall Lane Traffic Calming',
                'Roundhay Park Access Improvements',
                'Headingley Stadium Access Works',
                'Horsforth Junction Safety Scheme',
                'Seacroft Community Facilities Build',
                'Morley By-pass Minor Works',
                'Beeston Bridge Maintenance',
                'Otley Road Cycleway Extension',
                'Guiseley Drainage Upgrade'
            ]

            projects = []
            for title in project_titles:
                location = 'Leeds, UK' if not faker else f"{random.choice(['Leeds','Headingley','Horsforth','Seacroft','Morley','Beeston','Otley','Guiseley'])}, Leeds"
                description = faker.paragraph(nb_sentences=3) if faker else 'Project seed data.'
                image = 'https://images.unsplash.com/photo-1509395176047-4a66953fd231?auto=format&fit=crop&w=800&q=60'
                p, created = Project.objects.get_or_create(
                    title=title,
                    defaults={
                        'description': description,
                        'image': image,
                        'main_image': image,
                        'budget': random.choice([50000,100000,250000,500000,750000,1200000]),
                        'location': location,
                        'council': random.choice(councils),
                        'project_manager': faker.name() if faker else ''
                    }
                )
                projects.append(p)
            self.stdout.write(self.style.SUCCESS(f'Created/Loaded {len(projects)} projects'))

            self.stdout.write('Linking suppliers to projects...')
            link_count = 0
            for p in projects:
                chosen = random.sample(suppliers, k=random.randint(3,6))
                for s in chosen:
                    value = round(random.uniform(10000, 500000), 2)
                    ps, created = ProjectSupplier.objects.get_or_create(project=p, supplier=s, defaults={'contract_value': value})
                    if created:
                        link_count += 1
            self.stdout.write(self.style.SUCCESS(f'Created {link_count} project-supplier links'))

            # Seed some council meetings if none exist
            from supply_chain.models import CouncilMeeting
            existing_meetings = CouncilMeeting.objects.count()
            if existing_meetings == 0:
                self.stdout.write('Seeding council meetings...')
                import datetime
                meeting_count = 8
                locations = ['Council Chamber', 'Town Hall', 'Community Centre', 'Online (Zoom)', 'Library Meeting Room']
                for i in range(meeting_count):
                    # random date within next 60 days
                    days = random.randint(-7, 60)
                    date = datetime.date.today() + datetime.timedelta(days=days)
                    time = datetime.time(hour=random.choice([9,10,11,14,15,16]), minute=0)
                    loc = random.choice(locations)
                    agenda = (faker.sentence(nb_words=12) if faker else f'Agenda item {i+1}: discussion and updates')
                    CouncilMeeting.objects.create(council=random.choice(councils), date=date, time=time, location=loc, agenda=agenda)
                self.stdout.write(self.style.SUCCESS(f'Created {meeting_count} council meetings'))

            # Seed a few seasonal/community events if none exist
            from supply_chain.models import Event
            existing_events = Event.objects.count()
            if existing_events == 0:
                self.stdout.write('Seeding seasonal events...')
                import datetime
                today = datetime.date.today()
                year = today.year

                # Helper to compute US Thanksgiving (4th Thursday of November)
                def thanksgiving_date(y):
                    d = datetime.date(y, 11, 1)
                    # find first Thursday
                    first_thu = d + datetime.timedelta(days=(3 - d.weekday()) % 7)
                    # fourth Thursday is +21 days
                    return first_thu + datetime.timedelta(days=21)

                try:
                    tg = thanksgiving_date(year)
                except Exception:
                    tg = today + datetime.timedelta(days=7)

                # Christmas-themed multi-week attraction (use start date)
                christmas_start = datetime.date(year, 11, 21)
                new_year = datetime.date(year + 1, 1, 1)

                # Use a local image if available for hero visuals
                hero_image = 'supply_chain/static/img/projects/project_13.jpg'

                events_to_create = [
                    {
                        'title': 'Ice Cube at Christmas — festive rink & funfair',
                        'description': 'Celebrate the holiday season with a covered ice rink, festive food & drink stalls, and a family funfair running through the season.',
                        'date': christmas_start,
                        'location': 'City Centre Plaza',
                        'image': '/static/img/projects/project_13.jpg'
                    },
                    {
                        'title': 'Thanksgiving Community Lunch',
                        'description': 'Community Thanksgiving lunch and food bank drive. All welcome — bring a non-perishable donation.',
                        'date': tg,
                        'location': 'Community Centre',
                        'image': '/static/img/projects/project_30.jpg'
                    },
                    {
                        'title': 'New Year Celebration & Fireworks',
                        'description': 'Ring in the new year with a family-friendly fireworks display and live music.',
                        'date': new_year,
                        'location': 'Riverside Park',
                        'image': '/static/img/projects/project_42.jpg'
                    }
                ]

                for evdata in events_to_create:
                    Event.objects.create(
                        title=evdata['title'],
                        description=evdata['description'],
                        date=evdata['date'],
                        location=evdata['location'],
                        council=random.choice(councils),
                        image=evdata.get('image','')
                    )
                self.stdout.write(self.style.SUCCESS('Created seasonal events: Christmas, Thanksgiving, New Year'))

        self.stdout.write(self.style.SUCCESS('Seeding completed.'))
