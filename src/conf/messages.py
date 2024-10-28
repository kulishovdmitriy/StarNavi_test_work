# src/routes/comments

NO_COMMENTS_FOUND = "No comments found for post with id {post_id}"
NO_COMMENT_FOUND_FOR_POST = "No comment found with id {comment_id} for post with id {post_id}"
FAILED_TO_CREATE_COMMENT = "Failed to create comment"
FAILED_TO_UPDATE_COMMENT = "Failed to update comment"
COMMENT_NOT_FOUND_FOR_POST = "Comment with id {comment_id} not found for post {post_id}"
FAILED_TO_DELETE_COMMENT = "Failed to delete comment"
DATE_FROM_MUST_BE_LESS_OR_EQUAL_DATE_TO = "date_from must be less than or equal to date_to"
NO_COMMENTS_FOR_PERIOD = "No comments for this period {date_from} - {date_to}."

# src/routes/posts

NO_POSTS_FOUND = "No posts found"
POST_NOT_FOUND = "Post with id {post_id} not found"
TITLE_AND_CONTENT_REQUIRED = "Title and content are required"
FAILED_TO_CREATE_POST = "Failed to create post"
FAILED_TO_UPDATE_POST = "Failed to update post"
FAILED_TO_DELETE_POST = "Failed to delete post"

# src/repository/comments

COMMENT_CONTAINS_FORBIDDEN_WORDS = "Comment contains forbidden words and is blocked."
COMMENT_NOT_FOUND = "Comment with id {comment_id} not found"

# src/repository/posts

POST_CONTAINS_FORBIDDEN_WORDS = "Post contains forbidden words."

# main.py

DATABASE_CONNECTION_ERROR = "Error connecting to the database."
DATABASE_NOT_CONFIGURED = "Database is not configured correctly."
