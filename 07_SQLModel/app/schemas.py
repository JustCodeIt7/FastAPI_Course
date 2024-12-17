# schemas.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict, SecretStr
from uuid import UUID


class UserBase(BaseModel):
    """
    Represents a base user model for application usage.

    This class defines the structure of a user, including core attributes like
    `id`, `username`, and `email`, alongside optional fields for additional
    metadata. It ensures proper handling of user-related data within the application.

    :ivar id: Unique identifier for the user.
    :type id: UUID
    :ivar username: Username associated with the user.
    :type username: str
    :ivar email: Email address of the user.
    :type email: EmailStr
    :ivar full_name: Full name of the user.
    :type full_name: str
    :ivar bio: Optional short biography or description for the user.
    :type bio: Optional[str]
    :ivar created_at: Timestamp of when the user was created.
    :type created_at: datetime
    :ivar updated_at: Optional timestamp of when the user was last updated.
    :type updated_at: Optional[datetime]
    :ivar is_active: Indicates whether the user account is active.
    :type is_active: bool
    """

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    username: str
    email: EmailStr
    full_name: str
    bio: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool


class PostBase(BaseModel):
    """
    Represents the base structure for a post entity.

    This class serves as the foundational model for a post entity in the
    application. It captures essential attributes and metadata related to
    a post, including its identity, content, status, and ownership. The
    class leverages the `BaseModel` from Pydantic for data validation and
    parsing. It also uses a configuration enabling attribute-based
    instantiation. Subclasses can extend this class for more specialized
    post-related functionalities.

    :ivar id: Unique identifier for the post.
    :type id: UUID
    :ivar title: Title of the post.
    :type title: str
    :ivar content: Content/body of the post.
    :type content: str
    :ivar created_at: Timestamp indicating when the post was created.
    :type created_at: datetime
    :ivar updated_at: Timestamp indicating when the post was last updated.
        May be None if the post has never been updated.
    :type updated_at: Optional[datetime]
    :ivar published: Boolean flag indicating if the post is published
        (True) or is a draft (False).
    :type published: bool
    :ivar author_id: Unique identifier of the user who created the post.
    :type author_id: UUID
    """

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    published: bool
    author_id: UUID


class CommentBase(BaseModel):
    """
    Represents the base model for a comment in the system.

    This class defines the foundational structure for comments, including necessary
    fields and configurations for representing comment data in the system.

    :ivar id: Unique identifier for the comment.
    :type id: UUID
    :ivar content: The actual text content of the comment.
    :type content: str
    :ivar created_at: The datetime indicating when the comment was created.
    :type created_at: datetime
    :ivar updated_at: The datetime indicating when the comment was last updated, if
        applicable.
    :type updated_at: Optional[datetime]
    :ivar author_id: The unique identifier of the user who authored the comment.
    :type author_id: UUID
    :ivar post_id: The unique identifier of the post this comment is associated with.
    :type post_id: UUID
    """

    model_config = ConfigDict(from_attributes=True)
    id: UUID
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    author_id: UUID
    post_id: UUID


class UserCreate(BaseModel):
    """
    Class representing the creation of a user.

    This class is used to validate and store information needed for creating a user.
    It ensures that the provided data adheres to the required field constraints, such
    as minimum and maximum lengths for strings, optional fields, and validation of
    specific data types.

    :ivar username: The username of the user, which must have a minimum length of 3 and
        a maximum length of 50 characters.
    :type username: str
    :ivar email: The email address of the user which must adhere to standard email format.
    :type email: EmailStr
    :ivar full_name: The full name of the user, which must have a minimum length of 1 and
        a maximum length of 100 characters.
    :type full_name: str
    :ivar bio: An optional short biography of the user, with a maximum length of 500 characters.
    :type bio: Optional[str]
    :ivar password: The password of the user, stored as a secret string type for security purposes.
    :type password: SecretStr
    """

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    password: SecretStr


class PostCreate(BaseModel):
    """
    Defines the structure and constraints for creating a post.

    This class represents the schema required for creating a new post. It specifies
    the necessary fields, their constraints, and default values. Primarily used for
    data validation and enforcing consistency when handling new posts in an
    application.

    :ivar title: The title of the post, with constraints on minimum and maximum length.
    :type title: str
    :ivar content: The main content of the post, required and with a minimum length constraint.
    :type content: str
    :ivar published: Indicates whether the post is published. Defaults to False.
    :type published: bool
    """

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    published: bool = False


class CommentCreate(BaseModel):
    """
    Represents the creation of a user comment.

    This class is designed to model a comment provided by a user. It enforces
    constraints on the content's length and ensures a valid input according
    to the specified minimum and maximum length requirements. Typically used
    in scenarios where user-generated content needs to be validated before
    further processing or storage.

    :ivar content: The text content of the comment provided by the user.
        This value must meet the constraints of a minimum length of 1
        and a maximum length of 1000.
    :type content: str
    """

    content: str = Field(..., min_length=1, max_length=1000)


class Comment(CommentBase):
    """
    Represents a comment entity which inherits from the CommentBase class.

    This class provides additional functionality to represent and manage a
    user-generated comment. It is typically used to associate textual input
    with a specific context such as a blog post, article, or similar entities.

    :ivar author: The user who created the comment.
    :type author: UserBase
    """

    author: UserBase


class Post(PostBase):
    """
    Represents a post, typically used in a social media or blogging context.

    This class extends the PostBase, incorporating additional functionality
    to represent a post authored by a user and associated with multiple
    comments. It is designed to act as a data structure for content such as
    posts in a blog, social media platform, or similar application.

    :ivar author: The user who authored the post.
    :type author: UserBase
    :ivar comments: A list of comments associated with the post.
    :type comments: List[Comment]
    """

    author: UserBase
    comments: List[Comment] = []


class User(UserBase):
    """
    Represents a user and manages user-related information.

    This class extends the base user class and includes additional
    attributes to manage the user's posts and comments. It provides
    a structure for storing and organizing posts and comments created
    or associated with a user.

    :ivar posts: A list of posts created by the user.
    :type posts: List[Post]
    :ivar comments: A list of comments made by the user.
    :type comments: List[Comment]
    """

    posts: List[Post] = []
    comments: List[Comment] = []


class UserUpdate(BaseModel):
    """
    Represents a model for updating user details.

    This class is used for updating a user's information, such as username,
    email, full name, bio, and password. It validates input data and
    provides a structure for managing user update requests.

    :ivar username: The username of the user. Can be `None`. If provided, it should be a
        string with a minimum length of 3 and a maximum length of 50.
    :type username: Optional[str]
    :ivar email: The email address of the user. Can be `None`. Must follow the format of
        an email address.
    :type email: Optional[EmailStr]
    :ivar full_name: The full name of the user. Can be `None`. If provided, it should be a
        string with a minimum length of 1 and a maximum length of 100.
    :type full_name: Optional[str]
    :ivar bio: The bio or description of the user. Can be `None`. If provided, it should
        not exceed a length of 500.
    :type bio: Optional[str]
    :ivar password: The new password for the user. Can be `None`. The value must be
        securely handled as a `SecretStr`.
    :type password: Optional[SecretStr]
    """

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    password: Optional[SecretStr] = None
