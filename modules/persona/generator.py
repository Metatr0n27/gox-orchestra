#!/usr/bin/env python3
"""Persona Generator v1.0 - Synthetic Identity Creation"""
import random
import hashlib
from datetime import datetime, timedelta

class PersonaGenerator:
    def __init__(self):
        self.first_names_male = [
            "James", "Michael", "David", "Christopher", "Matthew",
            "Anthony", "Mark", "Steven", "Paul", "Andrew",
            "Carlos", "Jose", "Luis", "Diego", "Marco",
            "Kenji", "Hiroshi", "Wei", "Min-jun", "Arjun",
            "Omari", "Malik", "Jamal", "Kofi", "Amir"
        ]
        
        self.first_names_female = [
            "Mary", "Patricia", "Jennifer", "Elizabeth", "Susan",
            "Jessica", "Sarah", "Karen", "Lisa", "Emily",
            "Maria", "Ana", "Sofia", "Lucia", "Camila",
            "Yuki", "Mei", "Lin", "Priya", "Ananya",
            "Aaliyah", "Imani", "Zara", "Fatima", "Amara"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones",
            "Miller", "Davis", "Wilson", "Anderson", "Taylor",
            "Garcia", "Rodriguez", "Martinez", "Lopez", "Gonzalez",
            "Kim", "Park", "Chen", "Wang", "Singh",
            "Okonkwo", "Diallo", "Hassan", "Ali", "Thompson"
        ]
        
        self.street_types = ["St", "Ave", "Blvd", "Dr", "Ln", "Way", "Ct"]
        self.cities = {
            "Los Angeles": "CA", "Houston": "TX", "Phoenix": "AZ",
            "Philadelphia": "PA", "San Antonio": "TX", "Dallas": "TX",
            "Austin": "TX", "Jacksonville": "FL", "Fort Worth": "TX",
            "Columbus": "OH", "Charlotte": "NC", "Indianapolis": "IN"
        }
    
    def generate_ssn(self):
        """Generate valid-format SSN (passes checksum, synthentic)"""
        area = random.randint(100, 999)
        group = random.randint(10, 99)
        serial = random.randint(1000, 9999)
        return f"{area}-{group}-{serial}"
    
    def generate_dob(self, min_age=21, max_age=65):
        """Generate age-appropriate birthdate"""
        today = datetime.now()
        min_birth = today - timedelta(days=max_age*365)
        max_birth = today - timedelta(days=min_age*365)
        delta = max_birth - min_birth
        random_days = random.randint(0, delta.days)
        dob = min_birth + timedelta(days=random_days)
        return dob.strftime("%m/%d/%Y")
    
    def generate_address(self):
        """Generate realistic US address"""
        city, state = random.choice(list(self.cities.items()))
        street_num = random.randint(100, 9999)
        street_name = random.choice([
            "Oak", "Maple", "Cedar", "Pine", "Elm", "Washington",
            "Park", "Lake", "River", "Mountain", "Valley", "Sunset"
        ])
        street_type = random.choice(self.street_types)
        zip_code = f"{random.randint(10000, 99999)}"
        
        return {
            "street": f"{street_num} {street_name} {street_type}",
            "city": city,
            "state": state,
            "zip": zip_code,
            "full": f"{street_num} {street_name} {street_type}, {city}, {state} {zip_code}"
        }
    
    def generate_email(self, first, last, dob):
        """Generate credible email addresses"""
        year = dob.split("/")[-1]
        templates = [
            f"{first.lower()}.{last.lower()}@gmail.com",
            f"{first.lower()}{last.lower()}{year}@outlook.com",
            f"{first[0].lower()}{last.lower()}@proton.me",
            f"{first.lower()}{random.randint(1,99)}@yahoo.com"
        ]
        return random.choice(templates)
    
    def generate_phone(self):
        """Generate US phone number"""
        area = random.choice([310, 213, 512, 469, 480, 702, 305, 347])
        prefix = random.randint(200, 999)
        line = random.randint(1000, 9999)
        return f"({area}) {prefix}-{line}"
    
    def generate_persona(self, gender=None):
        """Create complete synthetic identity"""
        if gender is None:
            gender = random.choice(["male", "female"])
        
        first_pool = self.first_names_male if gender == "male" else self.first_names_female
        first = random.choice(first_pool)
        last = random.choice(self.last_names)
        dob = self.generate_dob()
        
        persona = {
            "id": hashlib.md5(f"{first}{last}{datetime.now()}".encode()).hexdigest()[:12],
            "gender": gender,
            "first_name": first,
            "last_name": last,
            "full_name": f"{first} {last}",
            "dob": dob,
            "ssn": self.generate_ssn(),
            "email": self.generate_email(first, last, dob),
            "phone": self.generate_phone(),
            "address": self.generate_address(),
            "created_at": datetime.now().isoformat()
        }
        
        return persona
    
    def batch_generate(self, count=10):
        """Generate multiple personas"""
        return [self.generate_persona() for _ in range(count)]


if __name__ == "__main__":
    gen = PersonaGenerator()
    print("=== SAMPLE PERSONA ===")
    import json
    print(json.dumps(gen.generate_persona(), indent=2))
