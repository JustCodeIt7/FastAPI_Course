# generate_data.py
from faker import Faker
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from main import BlogPost, Base, PostStatus

# Initialize Faker
fake = Faker()

# Database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def recreate_database():
    """Drop and recreate the database"""
    try:
        # Remove existing database file
        if os.path.exists("./blog.db"):
            os.remove("./blog.db")
        print("Removed existing database.")
    except Exception as e:
        print(f"Error removing database: {str(e)}")

    # Create new tables
    Base.metadata.create_all(bind=engine)
    print("Created new database with updated schema.")


def generate_random_date(start_date, end_date):
    """Generate a random datetime between start_date and end_date"""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)


def generate_random_author():
    """Generate a random author name"""
    return fake.name()


def generate_random_status():
    """Generate a random post status with weighted probabilities"""
    statuses = [
        (PostStatus.PUBLISHED, 0.7),
        (PostStatus.DRAFT, 0.2),
        (PostStatus.ARCHIVED, 0.1),
    ]
    return random.choices(
        [status for status, _ in statuses], weights=[weight for _, weight in statuses]
    )[0]


def generate_blog_posts(num_posts: int = 10):
    """Generate specified number of random blog posts"""
    db = SessionLocal()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)

    try:
        print(f"Generating {num_posts} random blog posts...")

        for i in range(num_posts):
            created_at = generate_random_date(start_date, end_date)
            updated_at = created_at + timedelta(days=random.randint(0, 30))

            base_title = fake.catch_phrase()
            title = f"{base_title} #{random.randint(1000, 9999)}"

            paragraphs = [fake.paragraph() for _ in range(random.randint(3, 7))]
            content = "\n\n".join(paragraphs)

            post = BlogPost(
                title=title,
                content=content,
                author=generate_random_author(),
                status=generate_random_status(),
                views=random.randint(0, 1000),
                created_at=created_at,
                updated_at=updated_at,
            )

            db.add(post)

            if (i + 1) % 10 == 0:
                print(f"Generated {i + 1} posts...")
                db.commit()

        db.commit()
        print("Successfully generated all blog posts!")

        print("\nDatabase Statistics:")
        total_posts = db.query(BlogPost).count()
        print(f"Total posts: {total_posts}")

        status_counts = {}
        for status in PostStatus:
            count = db.query(BlogPost).filter(BlogPost.status == status).count()
            status_counts[status.value] = count

        print("\nPosts by status:")
        for status, count in status_counts.items():
            print(f"{status}: {count}")

        sample_post = db.query(BlogPost).first()
        if sample_post:
            print("\nSample Post Preview:")
            print(f"Title: {sample_post.title}")
            print(f"Author: {sample_post.author}")
            print(f"Status: {sample_post.status}")
            print(f"Views: {sample_post.views}")
            print(f"Created: {sample_post.created_at}")
            print(f"Updated: {sample_post.updated_at}")
            print(f"Content Preview: {sample_post.content[:200]}...")

    except Exception as e:
        print(f"Error generating posts: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("This script will recreate the database with the updated schema.")
    should_proceed = input("Do you want to proceed? (y/n): ").lower()

    if should_proceed == "y":
        # Recreate database with new schema
        recreate_database()

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
    else:
        print("Operation cancelled.")
