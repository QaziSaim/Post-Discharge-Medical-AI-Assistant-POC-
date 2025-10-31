from faker import Faker   # will generate fake names and date
import random
import json

fake = Faker()

diagnoses = [
    "Diabetic Nephropathy",
    "Hypertensive Nephrosclerosis",
    "Nephrotic Syndrome"
]

medications = [
    ["Enalapril 5mg daily", "Spironolactone 25mg daily"],
    ["Atenolol 50mg daily", "Hydralazine 25mg twice daily"],
    ["Prednisolone 10mg daily", "Atorvastatin 20mg at night"]
]

diet_restrictions = [
    "Low protein (0.8g/kg/day), avoid sugary foods",
    "Low salt (1.5g/day), limited caffeine intake",
    "Low fat, moderate protein, avoid fried foods"
]

follow_ups = [
    "Lab review in 3 weeks",
    "BP check and renal function test in 1 week",
    "Nephrology follow-up in 10 days"
]

warning_signs = [
    "Sudden weight gain, ankle swelling",
    "Headache, blurred vision",
    "Foamy urine, persistent fatigue"
]


patients = []

for i in range(25):
    name = fake.name()
    date = fake.date_between(start_date='-180d', end_date='today').strftime('%Y-%m-%d')
    diagnosis = random.choice(diagnoses)
    meds = random.choice(medications)
    diet = random.choices(diet_restrictions)
    follow = random.choices(follow_ups)
    warning = random.choice(warning_signs)

    patient_report = {
        "patient_name":name,
        "discharge_date": date,
        "primary_diagnosis": diagnosis,
        "medications": meds,
        "dietary_restrictions": diet,
        "follow_up": follow,
        "warning_signs": warning,
        "discharge_instructions": "Monitor blood pressure daily and record body weight every morning."
    }

    patients.append(patient_report)

with open("patient_reports.json", "w") as f:
    json.dump(patients, f, indent=2)