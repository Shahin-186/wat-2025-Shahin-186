from django.core.management.base import BaseCommand
from supply_chain.models import Event, Council, Project
from datetime import date, time


class Command(BaseCommand):
    help = 'Update existing events with better images and create additional events'

    def handle(self, *args, **options):
        # Update existing events with better images
        events_updates = [
            {
                'id': 1,
                'image': '/static/img/projects/PARK.webp',
                'title': 'Ice Cube at Christmas — festive rink & funfair'
            },
            {
                'id': 2,
                'image': '/static/img/projects/project_13.jpg',
                'title': 'Thanksgiving Community Lunch'
            },
            {
                'id': 3,
                'image': '/static/img/projects/PARK.webp',
                'title': 'New Year Celebration & Fireworks'
            },
        ]

        for data in events_updates:
            try:
                event = Event.objects.get(id=data['id'])
                event.image = data['image']
                event.save()
                self.stdout.write(f"Updated event {data['id']}: {data['title']}")
            except Event.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Event {data['id']} not found"))

        # Create additional community events
        council = Council.objects.first()
        
        new_events = [
            {
                'title': 'Digital Skills Workshop',
                'description': 'Free workshop teaching basic digital skills for seniors and adults. Learn how to use smartphones, tablets, and online services safely.',
                'date': date(2025, 12, 10),
                'time': time(14, 0),
                'location': 'Community Centre',
                'image': '/static/img/projects/ICT CLASS.jpg',
                'council': council,
            },
            {
                'title': 'Youth Arts & Crafts Fair',
                'description': 'Showcase of local youth talent featuring art, crafts, music performances, and interactive workshops. Free entry for families.',
                'date': date(2025, 12, 15),
                'time': time(11, 0),
                'location': 'Town Hall',
                'image': '/static/img/projects/Art.jpg',
                'council': council,
            },
            {
                'title': 'Community Sports Day',
                'description': 'Annual sports day with activities for all ages. Football, basketball, athletics, and family relay races. Prizes and refreshments provided.',
                'date': date(2025, 12, 18),
                'time': time(10, 0),
                'location': 'Sports Centre',
                'image': '/static/img/projects/SPORTS HALL.jpeg',
                'council': council,
            },
            {
                'title': 'Nature Walk & Wildlife Talk',
                'description': 'Guided nature walk through local parks with an expert naturalist. Learn about local wildlife and conservation efforts.',
                'date': date(2025, 12, 22),
                'time': time(9, 30),
                'location': 'Park Entrance',
                'image': '/static/img/projects/WILDLIFE.webp',
                'council': council,
            },
            {
                'title': 'Public Transport Information Session',
                'description': 'Learn about new bus routes, schedules, and how to use the bus tracking system. Council transport team will answer your questions.',
                'date': date(2025, 12, 28),
                'time': time(15, 0),
                'location': 'Library Meeting Room',
                'image': '/static/img/projects/BUSES.jpg',
                'council': council,
            },
            {
                'title': 'Smart City WiFi Launch Event',
                'description': 'Official launch of free public WiFi across the city centre. Demonstrations and guidance on connecting your devices.',
                'date': date(2026, 1, 5),
                'time': time(12, 0),
                'location': 'City Centre Plaza',
                'image': '/static/img/projects/CITY WIFI.jpg',
                'council': council,
            },
        ]

        created_count = 0
        for event_data in new_events:
            event, created = Event.objects.get_or_create(
                title=event_data['title'],
                date=event_data['date'],
                defaults=event_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created event: {event.title}"))
            else:
                self.stdout.write(f"Event already exists: {event.title}")

        self.stdout.write(self.style.SUCCESS(f'\nCompleted. Created {created_count} new events.'))
