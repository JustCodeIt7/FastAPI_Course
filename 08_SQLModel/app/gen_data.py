import requests
import random
from faker import Faker
from typing import List, Dict
import time
from rich.console import Console
from rich.progress import track

console = Console()
fake = Faker()
BASE_URL = "http://localhost:8000"


class BlogDataGenerator:
    def __init__(self):
        self.users: List[Dict] = []
        self.posts: List[Dict] = []
        self.comments: List[Dict] = []

    def generate_user(self) -> Dict:
        """Generate fake user data"""
        return {
            "username": fake.user_name(),
            "email": fake.email(),
            "full_name": fake.name(),
            "bio": fake.text(max_nb_chars=200),
            "password": "password123",
        }

    def generate_post(self) -> Dict:
        """Generate fake post data"""
        return {
            "title": fake.catch_phrase(),
            "content": fake.paragraphs(nb=3).__str__(),
            "published": True,  # Added published field
        }

    def generate_comment(self) -> Dict:
        """Generate fake comment data"""
        return {"content": fake.paragraph()}

    def create_users(self, num_users: int = 5):
        """Create specified number of users"""
        console.print("\n[bold blue]Creating Users...[/bold blue]")

        for _ in track(range(num_users), description="Creating users..."):
            try:
                user_data = self.generate_user()
                response = requests.post(f"{BASE_URL}/users/", json=user_data)

                if response.status_code == 201:
                    user = response.json()
                    self.users.append(user)
                    console.print(f"[green]Created user:[/green] {user['username']}")
                else:
                    console.print(f"[red]Failed to create user:[/red] {response.text}")

                time.sleep(0.5)

            except Exception as e:
                console.print(f"[red]Error creating user:[/red] {str(e)}")

    def create_posts(self, posts_per_user: int = 3):
        """Create posts for each user"""
        console.print("\n[bold blue]Creating Posts...[/bold blue]")

        for user in self.users:
            for _ in track(
                range(posts_per_user), description=f"Creating posts for {user['username']}..."
            ):
                try:
                    post_data = self.generate_post()
                    response = requests.post(
                        f"{BASE_URL}/posts/", params={"user_id": user["id"]}, json=post_data
                    )

                    if response.status_code == 201:
                        post = response.json()
                        self.posts.append(post)
                        console.print(f"[green]Created post:[/green] {post['title'][:30]}...")
                    else:
                        console.print(f"[red]Failed to create post:[/red] {response.text}")

                    time.sleep(0.5)

                except Exception as e:
                    console.print(f"[red]Error creating post:[/red] {str(e)}")

    def create_comments(self, comments_per_post: int = 2):
        """Create comments for each post"""
        console.print("\n[bold blue]Creating Comments...[/bold blue]")

        for post in self.posts:
            for _ in track(
                range(comments_per_post), description=f"Creating comments for post {post['id']}"
            ):
                try:
                    random_user = random.choice(self.users)
                    comment_data = self.generate_comment()

                    response = requests.post(
                        f"{BASE_URL}/posts/{post['id']}/comments/",
                        params={"user_id": random_user["id"]},
                        json=comment_data,
                    )

                    if response.status_code == 201:
                        comment = response.json()
                        self.comments.append(comment)
                        console.print(
                            f"[green]Created comment for post {post['id'][:8]}...[/green]"
                        )
                    else:
                        console.print(f"[red]Failed to create comment:[/red] {response.text}")

                    time.sleep(0.5)

                except Exception as e:
                    console.print(f"[red]Error creating comment:[/red] {str(e)}")

    def print_statistics(self):
        """Print statistics about generated data"""
        console.print("\n[bold yellow]Generation Statistics[/bold yellow]")
        console.print(f"Total Users: {len(self.users)}")
        console.print(f"Total Posts: {len(self.posts)}")
        console.print(f"Total Comments: {len(self.comments)}")

    def generate_all(self, num_users=5, posts_per_user=3, comments_per_post=2):
        """Generate all data"""
        self.create_users(num_users)
        self.create_posts(posts_per_user)
        self.create_comments(comments_per_post)
        self.print_statistics()


def main():
    generator = BlogDataGenerator()
    generator.generate_all(num_users=3, posts_per_user=3, comments_per_post=2)


if __name__ == "__main__":
    main()
