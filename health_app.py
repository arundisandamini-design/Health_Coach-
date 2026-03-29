"""
Agentic AI-Based Health & Wellness Application
A comprehensive health management system with AI-powered recommendations
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import anthropic

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@dataclass
class UserProfile:
    """User profile data"""
    name: str
    age: int
    gender: str
    height_cm: float  # in centimeters
    weight_kg: float  # in kilograms
    health_goals: List[str]
    medical_conditions: List[str]
    allergies: List[str]
    activity_level: str  # sedentary, light, moderate, active, very_active

@dataclass
class DailyHealth:
    """Daily health tracking data"""
    date: str
    water_intake_ml: int
    meals_logged: List[Dict]
    workouts: List[Dict]
    meditation_minutes: int
    stress_level: int  # 1-10
    sleep_hours: float
    medication_taken: List[str]
    mood: str

class HealthWellnessApp:
    """Main health and wellness application with AI agent"""
    
    def __init__(self, data_dir: str = "health_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.user_profile_file = self.data_dir / "user_profile.json"
        self.daily_data_file = self.data_dir / "daily_health.json"
        self.medications_file = self.data_dir / "medications.json"
        self.user_profile = None
        self.daily_data = {}
        self.medications = []
        self.load_data()
        
    def load_data(self):
        """Load user profile and health data from files"""
        if self.user_profile_file.exists():
            with open(self.user_profile_file, 'r') as f:
                data = json.load(f)
                self.user_profile = UserProfile(**data)
        
        if self.daily_data_file.exists():
            with open(self.daily_data_file, 'r') as f:
                self.daily_data = json.load(f)
        
        if self.medications_file.exists():
            with open(self.medications_file, 'r') as f:
                self.medications = json.load(f)
    
    def save_data(self):
        """Save user profile and health data to files"""
        if self.user_profile:
            with open(self.user_profile_file, 'w') as f:
                json.dump(asdict(self.user_profile), f, indent=2)
        
        with open(self.daily_data_file, 'w') as f:
            json.dump(self.daily_data, f, indent=2)
        
        with open(self.medications_file, 'w') as f:
            json.dump(self.medications, f, indent=2)
    
    def setup_user_profile(self) -> UserProfile:
        """Interactive user profile setup"""
        print("\n" + "="*60)
        print("🏥 HEALTH & WELLNESS APP - USER SETUP")
        print("="*60)
        
        name = input("\nEnter your name: ").strip()
        age = int(input("Enter your age: "))
        
        print("\nGender (M/F/Other): ", end="")
        gender = input().strip()
        
        height_cm = float(input("Enter your height (in cm): "))
        weight_kg = float(input("Enter your weight (in kg): "))
        
        print("\nActivity level (sedentary/light/moderate/active/very_active): ", end="")
        activity_level = input().strip()
        
        print("\nHealth goals (comma-separated, e.g., weight loss, muscle gain, stress relief): ", end="")
        health_goals = [g.strip() for g in input().split(",")]
        
        print("\nMedical conditions (comma-separated, or press Enter if none): ", end="")
        medical_conditions = [c.strip() for c in input().split(",") if input().strip()]
        
        print("\nAllergies (comma-separated, or press Enter if none): ", end="")
        allergies = [a.strip() for a in input().split(",") if input().strip()]
        
        self.user_profile = UserProfile(
            name=name,
            age=age,
            gender=gender,
            height_cm=height_cm,
            weight_kg=weight_kg,
            health_goals=health_goals,
            medical_conditions=medical_conditions,
            allergies=allergies,
            activity_level=activity_level
        )
        
        self.save_data()
        print("\n✅ Profile created successfully!")
        return self.user_profile
    
    def calculate_bmi(self, weight_kg: float = None, height_cm: float = None) -> float:
        """Calculate BMI"""
        if weight_kg is None:
            weight_kg = self.user_profile.weight_kg
        if height_cm is None:
            height_cm = self.user_profile.height_cm
        
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 1)
    
    def get_bmi_category(self, bmi: float) -> str:
        """Get BMI category and health status"""
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal weight"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"
    
    def add_medication(self):
        """Add medication reminder"""
        print("\n" + "-"*40)
        print("💊 ADD MEDICATION")
        print("-"*40)
        
        name = input("Medication name: ").strip()
        dosage = input("Dosage (e.g., 500mg): ").strip()
        frequency = input("Frequency (e.g., twice daily, before meals): ").strip()
        times = input("Times to take (e.g., 08:00,14:00,20:00): ").strip()
        notes = input("Notes (optional): ").strip()
        
        medication = {
            "name": name,
            "dosage": dosage,
            "frequency": frequency,
            "times": times.split(","),
            "notes": notes,
            "added_date": datetime.now().isoformat()
        }
        
        self.medications.append(medication)
        self.save_data()
        print(f"✅ {name} added to medication list!")
    
    def check_medication_reminders(self) -> List[str]:
        """Check if any medications are due"""
        current_hour = datetime.now().strftime("%H:%M")
        reminders = []
        
        for med in self.medications:
            for time in med["times"]:
                if time.strip() == current_hour:
                    reminders.append(f"🔔 Time to take: {med['name']} ({med['dosage']})")
        
        return reminders
    
    def log_daily_health(self):
        """Log daily health metrics"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today in self.daily_data:
            print(f"\n⚠️  Already logged health data for today. View or update?")
            return
        
        print("\n" + "-"*40)
        print("📊 LOG TODAY'S HEALTH DATA")
        print("-"*40)
        
        water_ml = int(input("Water intake (ml): ") or "0")
        meditation_min = int(input("Meditation time (minutes): ") or "0")
        stress_level = int(input("Stress level (1-10): ") or "5")
        sleep_hours = float(input("Sleep hours: ") or "0")
        mood = input("Mood (happy/neutral/sad/anxious): ").strip()
        
        daily = DailyHealth(
            date=today,
            water_intake_ml=water_ml,
            meals_logged=[],
            workouts=[],
            meditation_minutes=meditation_min,
            stress_level=stress_level,
            sleep_hours=sleep_hours,
            medication_taken=[],
            mood=mood
        )
        
        self.daily_data[today] = asdict(daily)
        self.save_data()
        print("✅ Health data logged!")
    
    def track_water_intake(self):
        """Track daily water intake"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today not in self.daily_data:
            self.daily_data[today] = asdict(DailyHealth(
                date=today,
                water_intake_ml=0,
                meals_logged=[],
                workouts=[],
                meditation_minutes=0,
                stress_level=5,
                sleep_hours=0,
                medication_taken=[],
                mood="neutral"
            ))
        
        print("\n" + "-"*40)
        print("💧 WATER INTAKE TRACKER")
        print("-"*40)
        
        amount = int(input("How much water did you drink (ml)? "))
        self.daily_data[today]["water_intake_ml"] += amount
        
        total_today = self.daily_data[today]["water_intake_ml"]
        daily_goal = 2000  # 2 liters in ml
        percentage = (total_today / daily_goal) * 100
        
        print(f"\n💧 Water intake today: {total_today}ml / {daily_goal}ml ({percentage:.1f}%)")
        
        if total_today >= daily_goal:
            print("🎉 You've reached your daily water goal!")
        else:
            remaining = daily_goal - total_today
            print(f"⏳ You need {remaining}ml more water to reach your goal.")
        
        self.save_data()
    
    def ai_agent_recommendation(self, user_input: str) -> str:
        """Get AI-powered recommendations using Claude"""
        
        # Prepare context
        context = self._prepare_context()
        
        system_prompt = """You are a sophisticated AI Health & Wellness Agent. Your role is to:
1. Provide personalized health advice based on user profile and health data
2. Recommend customized workout plans aligned with fitness goals
3. Suggest balanced, nutritious meal plans considering allergies and preferences
4. Guide meditation and stress management techniques
5. Monitor medication adherence and health metrics
6. Track BMI and provide weight management advice
7. Remind users to stay hydrated and maintain healthy habits

Be conversational, empathetic, and provide actionable advice. Always consider the user's medical conditions and allergies."""
        
        messages = [
            {
                "role": "user",
                "content": f"""User Context:
{context}

User Request: {user_input}

Please provide a thoughtful, personalized response."""
            }
        ]
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=messages
        )
        
        return response.content[0].text
    
    def _prepare_context(self) -> str:
        """Prepare user context for AI"""
        if not self.user_profile:
            return "No user profile set up yet."
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_data = self.daily_data.get(today, {})
        
        bmi = self.calculate_bmi()
        bmi_category = self.get_bmi_category(bmi)
        
        context = f"""
Name: {self.user_profile.name}
Age: {self.user_profile.age}
Gender: {self.user_profile.gender}
Height: {self.user_profile.height_cm}cm
Weight: {self.user_profile.weight_kg}kg
BMI: {bmi} ({bmi_category})
Activity Level: {self.user_profile.activity_level}
Health Goals: {', '.join(self.user_profile.health_goals)}
Medical Conditions: {', '.join(self.user_profile.medical_conditions) if self.user_profile.medical_conditions else 'None'}
Allergies: {', '.join(self.user_profile.allergies) if self.user_profile.allergies else 'None'}

Today's Health Data:
- Water Intake: {today_data.get('water_intake_ml', 0)}ml
- Meditation: {today_data.get('meditation_minutes', 0)} minutes
- Stress Level: {today_data.get('stress_level', 5)}/10
- Sleep: {today_data.get('sleep_hours', 0)} hours
- Mood: {today_data.get('mood', 'Not logged')}

Current Medications: {len(self.medications)} medications tracked
"""
        return context
    
    def get_personalized_workout_plan(self):
        """Get AI-generated personalized workout plan"""
        print("\n" + "-"*40)
        print("💪 PERSONALIZED WORKOUT PLAN")
        print("-"*40)
        
        duration = input("How many days per week can you exercise? (1-7): ").strip()
        preference = input("Exercise preference (cardio/strength/yoga/mixed): ").strip()
        
        prompt = f"""Create a detailed {duration}-day per week {preference} workout plan for someone with my profile. 
Include:
- Specific exercises with sets and reps
- Rest days and recovery tips
- Progression guidelines
- Safety considerations"""
        
        response = self.ai_agent_recommendation(prompt)
        print("\n" + response)
        return response
    
    def get_meal_plan(self):
        """Get AI-generated personalized meal plan"""
        print("\n" + "-"*40)
        print("🍽️  PERSONALIZED MEAL PLAN")
        print("-"*40)
        
        duration = input("How many days for meal plan? (3/7/14): ").strip()
        cuisine = input("Preferred cuisines (comma-separated): ").strip()
        restrictions = input("Dietary restrictions (comma-separated or none): ").strip()
        
        prompt = f"""Create a detailed {duration}-day personalized meal plan with:
- Calorie targets appropriate for my activity level
- Macronutrient breakdown
- Meal recipes with ingredients
- Grocery shopping list
- Hydration guidelines
Preferences: {cuisine}
Restrictions: {restrictions if restrictions else 'None'}"""
        
        response = self.ai_agent_recommendation(prompt)
        print("\n" + response)
        return response
    
    def get_stress_management(self):
        """Get stress management and meditation guidance"""
        print("\n" + "-"*40)
        print("🧘 STRESS MANAGEMENT & MEDITATION")
        print("-"*40)
        
        current_stress = int(input("Current stress level (1-10): "))
        available_time = int(input("Available time for session (minutes): "))
        
        prompt = f"""My current stress level is {current_stress}/10 and I have {available_time} minutes available.
Please provide:
1. A guided {available_time}-minute meditation or breathing exercise
2. Specific stress management techniques for my situation
3. Long-term stress reduction strategies
4. Signs I should take a break
5. When to seek professional help"""
        
        response = self.ai_agent_recommendation(prompt)
        print("\n" + response)
        return response
    
    def get_health_tips(self):
        """Get general health advice"""
        print("\n" + "-"*40)
        print("💡 PERSONALIZED HEALTH TIPS")
        print("-"*40)
        
        topic = input("What health topic? (nutrition/fitness/sleep/mental health/general): ").strip()
        
        prompt = f"""Provide 5 actionable health tips for {topic} that are specifically tailored to my profile and goals.
Make them practical and easy to implement."""
        
        response = self.ai_agent_recommendation(prompt)
        print("\n" + response)
        return response
    
    def view_health_summary(self):
        """View comprehensive health summary"""
        print("\n" + "="*60)
        print("📋 HEALTH SUMMARY")
        print("="*60)
        
        if not self.user_profile:
            print("No user profile set up yet.")
            return
        
        print(f"\nProfile: {self.user_profile.name}")
        print(f"Age: {self.user_profile.age} | Gender: {self.user_profile.gender}")
        print(f"Height: {self.user_profile.height_cm}cm | Weight: {self.user_profile.weight_kg}kg")
        
        bmi = self.calculate_bmi()
        bmi_category = self.get_bmi_category(bmi)
        print(f"\n📊 BMI: {bmi} - {bmi_category}")
        
        print(f"Activity Level: {self.user_profile.activity_level}")
        print(f"Health Goals: {', '.join(self.user_profile.health_goals)}")
        
        if self.user_profile.medical_conditions:
            print(f"Medical Conditions: {', '.join(self.user_profile.medical_conditions)}")
        
        if self.user_profile.allergies:
            print(f"Allergies: {', '.join(self.user_profile.allergies)}")
        
        print(f"\n💊 Medications: {len(self.medications)}")
        for med in self.medications:
            print(f"  - {med['name']} ({med['dosage']}) - {med['frequency']}")
        
        today = datetime.now().strftime("%Y-%m-%d")
        if today in self.daily_data:
            data = self.daily_data[today]
            print(f"\n📅 Today's Data ({today}):")
            print(f"  - Water: {data['water_intake_ml']}ml / 2000ml")
            print(f"  - Meditation: {data['meditation_minutes']} minutes")
            print(f"  - Stress: {data['stress_level']}/10")
            print(f"  - Sleep: {data['sleep_hours']} hours")
            print(f"  - Mood: {data['mood']}")
    
    def run(self):
        """Main application loop"""
        print("\n" + "="*60)
        print("🏥 WELCOME TO AI HEALTH & WELLNESS APP")
        print("="*60)
        
        if not self.user_profile:
            self.setup_user_profile()
        
        while True:
            print("\n" + "-"*60)
            print("MAIN MENU")
            print("-"*60)
            print("1. View Health Summary")
            print("2. Log Daily Health Data")
            print("3. Track Water Intake")
            print("4. Add/View Medications")
            print("5. Get Personalized Workout Plan")
            print("6. Get Meal Plan")
            print("7. Stress Management & Meditation")
            print("8. Get Health Tips")
            print("9. Chat with AI Health Agent")
            print("10. Check Medication Reminders")
            print("11. Update Profile")
            print("12. Exit")
            print("-"*60)
            
            choice = input("Select option (1-12): ").strip()
            
            if choice == "1":
                self.view_health_summary()
            elif choice == "2":
                self.log_daily_health()
            elif choice == "3":
                self.track_water_intake()
            elif choice == "4":
                sub_choice = input("Add medication (A) or View (V)? ").upper()
                if sub_choice == "A":
                    self.add_medication()
                else:
                    print("\nYour Medications:")
                    for med in self.medications:
                        print(f"- {med['name']} ({med['dosage']}) - {med['frequency']}")
            elif choice == "5":
                self.get_personalized_workout_plan()
            elif choice == "6":
                self.get_meal_plan()
            elif choice == "7":
                self.get_stress_management()
            elif choice == "8":
                self.get_health_tips()
            elif choice == "9":
                user_input = input("\nWhat would you like to know about your health? ")
                response = self.ai_agent_recommendation(user_input)
                print("\n" + response)
            elif choice == "10":
                reminders = self.check_medication_reminders()
                if reminders:
                    for reminder in reminders:
                        print(reminder)
                else:
                    print("No medication reminders at this time.")
            elif choice == "11":
                self.setup_user_profile()
            elif choice == "12":
                print("\n👋 Thank you for using Health & Wellness App. Stay healthy!")
                break
            else:
                print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    app = HealthWellnessApp()
    app.run()