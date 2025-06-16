from app import db, app  # Make sure this matches your app's import path
from models import User, Profile, Todo
from faker import Faker
import random

fake = Faker()

def seed_data():
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()

        users = []
        profiles = []
        todos = []

        # Create 5 users and associated profiles
        for _ in range(5):
            email = fake.email()
            user = User(email=email)
            user.set_password("C0743250838c")  # Use your model's method to hash password
            db.session.add(user)
            db.session.flush()  # Get user.id without commit

            profile = Profile(
                username=fake.user_name(),
                bio=fake.sentence(nb_words=10),
                profile_picture_url=fake.image_url(),
                user_id=user.id
            )
            users.append(user)
            profiles.append(profile)
            db.session.add(profile)

        # Create 10 todos (2 for each user)
        for user in users:
            for _ in range(2):
                todo = Todo(
                    content=fake.sentence(nb_words=6),
                    user_id=user.id
                )
                todos.append(todo)
                db.session.add(todo)

        # Commit all to database
        db.session.commit()

        print("✅ Seeded 5 users, 5 profiles, 10 todos.")

if __name__ == "__main__":
    seed_data()
