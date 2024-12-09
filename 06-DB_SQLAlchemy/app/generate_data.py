# generate_data.py
from faker import Faker
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import BlogPost, Base

# Initialize Faker
fake = Faker()

# Database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure tables exist
Base.metadata.create_all(bind=engine)

def generate_random_date(start_date, end_date):
    """Generate a random datetime between start_date and end_date"""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def generate_blog_posts(num_posts: int = 100):
    """Generate specified number of random blog posts"""
    db = SessionLocal()

    # Date range for posts (last 2 years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years ago

    try:
        print(f"Generating {num_posts} random blog posts...")

        for i in range(num_posts):
            # Generate random post data
            title = fake.catch_phrase()

            # Generate content with multiple paragraphs
            paragraphs = [fake.paragraph() for _ in range(random.randint(3, 7))]
            content = "\n\n".join(paragraphs)

            # Generate random date
            created_at = generate_random_date(start_date, end_date)

            # Create post
            post = BlogPost(
                title=title,
                content=content,
                created_at=created_at
            )

            db.add(post)

            # Print progress
            if (i + 1) % 10 == 0:
                print(f"Generated {i + 1} posts...")

                # Commit all posts to database
        db.commit()
        print("Successfully generated all blog posts!")

        # Print some statistics
        total_posts = db.query(BlogPost).count()
        print(f"\nDatabase Statistics:")
        print(f"Total posts in database: {total_posts}")

        # Sample post preview
        sample_post = db.query(BlogPost).first()
        print("\nSample Post Preview:")
        print(f"Title: {sample_post.title}")
        print(f"Created: {sample_post.created_at}")
        print(f"Content Preview: {sample_post.content[:200]}...")

    except Exception as e:
        print(f"Error generating posts: {str(e)}")
        db.rollback()
    finally:
        db.close()

def clear_database():
    """Clear all existing posts from the database"""
    db = SessionLocal()
    try:
        print("Clearing existing posts...")
        db.query(BlogPost).delete()
        db.commit()
        print("Database cleared successfully!")
    except Exception as e:
        print(f"Error clearing database: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Ask user if they want to clear existing data
    should_clear = input("Do you want to clear existing posts? (y/n): ").lower()
    if should_clear == 'y':
        clear_database()

        # Get number of posts to generate
    while True:
        try:
            num_posts = int(input("How many posts do you want to generate? "))
            if num_posts > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")

            # Generate posts
    generate_blog_posts(num_posts)