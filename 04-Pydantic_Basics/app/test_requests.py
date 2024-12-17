from faker import Faker
import random

# Import necessary parts from your main app
from main import PostCreate, PostStatus, posts_db, post_id_counter, Post  # Ensure you import the Post class

fake = Faker()

def generate_fake_post():
    title = fake.sentence(nb_words=random.randint(5, 10)).strip('.')
    content = fake.text(max_nb_chars=200)
    author = fake.name()
    status = random.choice(list(PostStatus))
    
    return PostCreate(
        title=title,
        content=content,
        author=author,
        status=status
    )

def populate_database(num_posts):
    global post_id_counter
    
    for _ in range(num_posts):
        new_post = generate_fake_post()
        
        # Check for duplicate titles (this is a simple check and might not be efficient for large datasets)
        while any(p.title == new_post.title for p in posts_db.values()):
            new_post.title = fake.sentence(nb_words=random.randint(5, 10)).strip('.')
        
        # Use a different variable name to avoid conflict
        post_instance = Post(
            id=post_id_counter,
            **new_post.dict()
        )
        posts_db[post_id_counter] = post_instance
        post_id_counter += 1

if __name__ == "__main__":
    # Generate and populate the database with 10 fake posts
    populate_database(10)
    
    # Print out the generated posts to verify
    for post in posts_db.values():
        print(post.dict())
