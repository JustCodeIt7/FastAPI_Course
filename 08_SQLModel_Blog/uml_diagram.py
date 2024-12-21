from graphviz import Digraph


# Update the diagram with relationship details
uml_diagram = Digraph("UML_Diagram_Relationships", format="png")
# Define global styles for a dark theme


# User model
uml_diagram.node(
    "User",
    """{
    User |
    id: UUID |
    username: str |
    email: EmailStr |
    full_name: str |
    bio: Optional[str] |
    created_at: datetime |
    updated_at: Optional[datetime] |
    is_active: bool |
    posts: List[Post] |
    comments: List[Comment]
}""",
)

# Post model
uml_diagram.node(
    "Post",
    """{
    Post |
    id: UUID |
    title: str |
    content: str |
    created_at: datetime |
    updated_at: Optional[datetime] |
    published: bool |
    author_id: UUID |
    author: User |
    comments: List[Comment]
}""",
)

# Comment model
uml_diagram.node(
    "Comment",
    """{
    Comment |
    id: UUID |
    content: str |
    created_at: datetime |
    updated_at: Optional[datetime] |
    author_id: UUID |
    post_id: UUID |
    author: User |
    post: Post
}""",
)

# Relationships with cardinality details
uml_diagram.edge("User", "Post", label="1 to Many (posts)", dir="forward")
uml_diagram.edge("User", "Comment", label="1 to Many (comments)", dir="forward")
uml_diagram.edge("Post", "Comment", label="1 to Many (comments)", dir="forward")
uml_diagram.edge("Post", "User", label="Many to 1 (author)", dir="forward")
uml_diagram.edge("Comment", "User", label="Many to 1 (author)", dir="forward")
uml_diagram.edge("Comment", "Post", label="Many to 1 (post)", dir="forward")

# Render the updated diagram
uml_diagram.render("./sql_model_uml_with_relationships", view=False)
