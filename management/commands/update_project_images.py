from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Update duplicate project titles and attach relevant static images'

    def handle(self, *args, **options):
        from supply_chain.models import Project

        # Images available in static: choose a small set for assignment
        imgs = [
            '/static/img/projects/project_11.jpg',
            '/static/img/projects/project_14.jpg',
            '/static/img/projects/project_15.jpg',
            '/static/img/projects/project_16.jpg',
            '/static/img/projects/project_17.jpg',
            '/static/img/projects/project_19.jpg',
        ]

        duplicates = Project.objects.filter(title__icontains='East Leeds Road Resurfacing')
        if not duplicates.exists():
            self.stdout.write(self.style.NOTICE('No projects matching "East Leeds Road Resurfacing" found.'))
            return

        self.stdout.write(f'Found {duplicates.count()} matching projects; updating titles and images...')

        for i, proj in enumerate(duplicates):
            # Give each project a unique section suffix if duplicates exist
            new_title = proj.title
            # If title already ends with a number, remove it
            if proj.title.strip().endswith('11'):
                base = proj.title.strip().rsplit('11', 1)[0].strip()
                base = base.rstrip('-–:')
            else:
                base = proj.title

            # Create a nicer unique title
            new_title = f"{base} — Section {i+1}"
            proj.title = new_title

            # Assign a related image from the pool (cycle if needed)
            img = imgs[i % len(imgs)]
            proj.main_image = img
            proj.image = img

            proj.save()
            self.stdout.write(self.style.SUCCESS(f'Updated project id={proj.id} title="{proj.title}" image={img}'))

        self.stdout.write(self.style.SUCCESS('Update complete.'))
