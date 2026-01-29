from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Replace all projects and create councils/categories from a provided static list.'

    def handle(self, *args, **options):
        import datetime
        from django.db import transaction
        from supply_chain.models import Project, Council, Category
        from django.conf import settings

        data = [
            # title, council, category, budget, created_at_string
            ("New City Library Digital Hub", "North Ward Authority", "Community Facilities", "$890,500", "14 Nov 2025, 1:20 p.m."),
            ("University Research Grant Fund", "Northern Regional EDU", "University Funding", "$1,750,000", "28 Sep 2024, 10:15 a.m."),
            ("Buses: Electric Fleet Conversion", "Metropolitan Transport", "Public Transport", "$4,300,000", "05 Dec 2023, 7:45 p.m."),
            ("Primary School ICT Equipment Rollout", "South District Council", "School Funding", "$320,800", "17 Oct 2025, 9:01 a.m."),
            ("City Park Wildlife Habitat Restoration", "Green Spaces Trust", "Parks & Green Spaces", "$450,250", "03 Jan 2024, 2:30 p.m."),
            ("Heritage Building Facade Renewal", "Central Business Group", "Heritage & Culture", "$1,150,000", "21 May 2023, 11:10 a.m."),
            ("Youth Services Outreach Programme", "West End Borough", "Social Services", "$285,000", "19 Jul 2025, 4:55 p.m."),
            ("Secondary School Sports Hall Upgrade", "East Village Authority", "School Funding", "$950,000", "09 Mar 2023, 8:15 a.m."),
            ("City-Wide Free Wi-Fi Implementation", "City Technology Board", "Digital Infrastructure", "$2,100,000", "01 Apr 2024, 11:40 a.m."),
            ("Buses: New Express Route Feasibility Study", "Metropolitan Transport", "Public Transport", "$120,000", "25 Feb 2025, 3:05 p.m."),
            ("Local Arts & Culture Festival Funding", "Arts & Events Commission", "Arts & Events", "$60,500", "12 Jun 2023, 9:50 p.m."),
            ("University Student Accommodation Build", "Northern Regional EDU", "University Funding", "$5,500,000", "30 Sep 2025, 6:20 a.m."),
            ("Park Playground Equipment Modernisation", "Green Spaces Trust", "Parks & Green Spaces", "$185,900", "20 Aug 2024, 10:00 a.m."),
            ("Apprenticeship Training Scheme Launch", "Economic Growth Agency", "Economic Development", "$700,000", "11 Jan 2025, 1:15 p.m."),
            ("Buses: Real-Time Tracking System", "Metropolitan Transport", "Public Transport", "$510,000", "08 Feb 2024, 12:45 p.m."),
        ]

        # find some static images to assign (cycle through them)
        import glob, os
        static_images = glob.glob(os.path.join(settings.BASE_DIR, 'supply_chain', 'static', 'img', 'projects', '*.jpg'))
        if not static_images:
            # fallback to empty list
            static_images = []

        with transaction.atomic():
            # remove existing projects
            Project.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Deleted existing projects.'))

            # create councils & categories, then projects
            councils_cache = {}
            categories_cache = {}

            for idx, (title, council_name, category_name, budget_str, created_str) in enumerate(data):
                # create/get council
                council = councils_cache.get(council_name)
                if not council:
                    council, _ = Council.objects.get_or_create(name=council_name, defaults={
                        'contact': council_name,
                        'contact_email': f'info@{council_name.lower().replace(" ","")}.gov'
                    })
                    councils_cache[council_name] = council

                # create/get category
                category = categories_cache.get(category_name)
                if not category:
                    category, _ = Category.objects.get_or_create(name=category_name)
                    categories_cache[category_name] = category

                # parse budget (strip $ and commas)
                try:
                    budget = int(budget_str.replace('$', '').replace(',', '').strip())
                except Exception:
                    budget = 0

                # parse created datetime
                s = created_str.replace('.', '').replace('a m', 'AM').replace('p m', 'PM')
                s = s.replace('a.m', 'AM').replace('p.m', 'PM').replace('am', 'AM').replace('pm', 'PM')
                try:
                    created_dt = datetime.datetime.strptime(s, '%d %b %Y, %I:%M %p')
                except Exception:
                    # fallback to today
                    created_dt = datetime.datetime.now()

                # assign an image (use static relative path)
                img = ''
                if static_images:
                    img_path = static_images[idx % len(static_images)]
                    # convert absolute path to static URL path
                    # static file location is supply_chain/static/... so we want /static/...
                    parts = img_path.split(os.path.sep)
                    try:
                        static_index = parts.index('static')
                        img = '/' + '/'.join(parts[static_index:])
                    except ValueError:
                        img = img_path

                proj = Project.objects.create(
                    title=title,
                    description=f"{title} — category: {category_name}",
                    image=img,
                    main_image=img,
                    category=category,
                    budget=budget,
                    project_manager='',
                    location='',
                    council=council,
                )

                # update created_at to the parsed date
                Project.objects.filter(pk=proj.pk).update(created_at=created_dt)
                self.stdout.write(self.style.SUCCESS(f'Created project: {title} (council={council_name})'))

        self.stdout.write(self.style.SUCCESS('Seeding of custom projects complete.'))
