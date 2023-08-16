import datetime

def generate_wedding_plan(budget):
    today = datetime.date.today()
    
    events = [
        {
            "key": "sangeet",
            "event": "Sangeet Ceremony",
            "date": (today + datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
            "venue": "Grand Ballroom, ABC Hotel",
            "time": "6:00 PM",
            "budget": budget * 0.2
        },
        {
            "key": "mehendi",
            "event": "Mehendi Ceremony",
            "date": (today + datetime.timedelta(days=8)).strftime('%Y-%m-%d'),
            "venue": "Poolside Lawn, XYZ Resort",
            "time": "11:00 AM",
            "budget": budget * 0.15
        },
        {
            "key": "haldi",
            "event": "Haldi Ceremony",
            "date": (today + datetime.timedelta(days=9)).strftime('%Y-%m-%d'),
            "venue": "Backyard Garden, Family Residence",
            "time": "9:00 AM",
            "budget": budget * 0.1
        },
        {
            "key": "wedding",
            "event": "Wedding Ceremony",
            "date": (today + datetime.timedelta(days=10)).strftime('%Y-%m-%d'),
            "venue": "Royal Palace, City Center",
            "time": "7:00 PM",
            "budget": budget * 0.5
        },
        {
            "key": "reception",
            "event": "Reception",
            "date": (today + datetime.timedelta(days=11)).strftime('%Y-%m-%d'),
            "venue": "Luxury Banquet Hall, Downtown",
            "time": "8:00 PM",
            "budget": budget * 0.25
        }
    ]
    
    response = {"events": events}
    return response
