import os
import urllib.request

from django.core.files import File
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Download images for Events that lack an uploaded image_file. Uses event.image URL or picsum.photos as fallback.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=20, help='Maximum number of events to process')

    def handle(self, *args, **options):
        from supply_chain.models import Event
        limit = options.get('limit')
        qs = Event.objects.filter(image_file__isnull=True)[:limit]
        if not qs:
            self.stdout.write('No events need images.')
            return

        tmp_dir = '/tmp/event_image_downloads'
        os.makedirs(tmp_dir, exist_ok=True)

        count = 0
        for i, ev in enumerate(qs):
            # prefer an explicit image URL if present
            url = ev.image if ev.image else f'https://picsum.photos/1200/800?random={ev.pk}'
            try:
                fname = os.path.join(tmp_dir, f'event_{ev.pk}.jpg')
                # download to temporary file
                urllib.request.urlretrieve(url, fname)
                with open(fname, 'rb') as f:
                    ev.image_file.save(os.path.basename(fname), File(f), save=True)
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Attached image to Event {ev.pk}'))
            except Exception as e:
                self.stderr.write(f'Failed to fetch image for Event {ev.pk}: {e}')

        # cleanup (leave files for inspection is fine, but remove to be tidy)
        try:
            for fn in os.listdir(tmp_dir):
                os.remove(os.path.join(tmp_dir, fn))
            os.rmdir(tmp_dir)
        except Exception:
            pass

        self.stdout.write(self.style.SUCCESS(f'Completed. {count} events updated.'))
