"""
Script to populate sample venues in the database
Run this script to add pre-defined venues for event creation
"""
import sys
from app import create_app
from models import db, Venue

def populate_venues():
    """Populate database with sample venues"""
    app = create_app('development')
    
    with app.app_context():
        # Check if venues already exist
        existing_venues = Venue.query.count()
        if existing_venues >= 8:
            print(f"[INFO] {existing_venues} venues already exist in the database.")
            print("[INFO] Skipping venue population. Venues are already populated.")
            return
        elif existing_venues > 0:
            print(f"[INFO] {existing_venues} venues already exist. Adding sample venues...")
        
        venues_data = [
            {
                'venue_name': 'Grand Convention Center',
                'address': '123 Main Street',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'postal_code': '10001',
                'capacity': 5000,
                'description': 'A spacious convention center in the heart of Manhattan, perfect for large-scale events, conferences, and exhibitions.',
                'amenities': ['WiFi', 'Parking', 'Catering', 'Audio/Visual Equipment', 'Accessibility']
            },
            {
                'venue_name': 'Riverside Music Hall',
                'address': '456 River Road',
                'city': 'Los Angeles',
                'state': 'CA',
                'country': 'USA',
                'postal_code': '90028',
                'capacity': 2500,
                'description': 'An iconic music venue with state-of-the-art sound systems and lighting, ideal for concerts and live performances.',
                'amenities': ['WiFi', 'Parking', 'Bar', 'Sound System', 'Lighting']
            },
            {
                'venue_name': 'Sports Arena Complex',
                'address': '789 Stadium Boulevard',
                'city': 'Chicago',
                'state': 'IL',
                'country': 'USA',
                'postal_code': '60601',
                'capacity': 10000,
                'description': 'A modern multi-purpose sports arena capable of hosting sports events, concerts, and large gatherings.',
                'amenities': ['WiFi', 'Parking', 'Concessions', 'Accessibility', 'VIP Suites']
            },
            {
                'venue_name': 'Downtown Theater',
                'address': '321 Arts District',
                'city': 'San Francisco',
                'state': 'CA',
                'country': 'USA',
                'postal_code': '94102',
                'capacity': 800,
                'description': 'An elegant theater with excellent acoustics, perfect for theatrical performances, lectures, and intimate concerts.',
                'amenities': ['WiFi', 'Parking', 'Bar', 'Accessibility', 'Dressing Rooms']
            },
            {
                'venue_name': 'Exhibition Hall',
                'address': '654 Trade Center Drive',
                'city': 'Miami',
                'state': 'FL',
                'country': 'USA',
                'postal_code': '33101',
                'capacity': 3000,
                'description': 'A versatile exhibition space with modular layout options, suitable for trade shows, exhibitions, and corporate events.',
                'amenities': ['WiFi', 'Parking', 'Catering', 'Loading Dock', 'Meeting Rooms']
            },
            {
                'venue_name': 'Beachside Pavilion',
                'address': '987 Ocean View Drive',
                'city': 'San Diego',
                'state': 'CA',
                'country': 'USA',
                'postal_code': '92101',
                'capacity': 1500,
                'description': 'An open-air pavilion with stunning ocean views, perfect for outdoor concerts, festivals, and celebrations.',
                'amenities': ['WiFi', 'Parking', 'Bar', 'Outdoor Stage', 'Restrooms']
            },
            {
                'venue_name': 'University Auditorium',
                'address': '147 Campus Way',
                'city': 'Boston',
                'state': 'MA',
                'country': 'USA',
                'postal_code': '02115',
                'capacity': 1200,
                'description': 'A prestigious academic venue with excellent facilities for lectures, conferences, and cultural events.',
                'amenities': ['WiFi', 'Parking', 'Projection Equipment', 'Accessibility', 'Recording Studio']
            },
            {
                'venue_name': 'Jazz Club Downtown',
                'address': '258 Music Street',
                'city': 'New Orleans',
                'state': 'LA',
                'country': 'USA',
                'postal_code': '70112',
                'capacity': 300,
                'description': 'An intimate jazz club with a rich history, featuring live music performances in an atmospheric setting.',
                'amenities': ['WiFi', 'Bar', 'Sound System', 'Stage', 'Seating']
            }
        ]
        
        created_count = 0
        for venue_data in venues_data:
            # Check if venue already exists
            existing = Venue.query.filter_by(
                venue_name=venue_data['venue_name'],
                city=venue_data['city']
            ).first()
            
            if not existing:
                venue = Venue(**venue_data)
                db.session.add(venue)
                created_count += 1
                print(f"[OK] Added venue: {venue_data['venue_name']} in {venue_data['city']}")
            else:
                print(f"[SKIP] Venue already exists: {venue_data['venue_name']} in {venue_data['city']}")
        
        try:
            db.session.commit()
            print(f"\n[SUCCESS] Successfully added {created_count} venues to the database!")
            print(f"[INFO] Total venues in database: {Venue.query.count()}")
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Error adding venues: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    populate_venues()

