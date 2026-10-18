from dataclasses import dataclass
from functools import partial

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from backend.blog.models import Post, Comment
from backend.blog.repository import PostRepository, CommentRepository


@dataclass
class BlogLoaders:
    posts_by_author: DataLoader[int, list[Post]]
    posts_count_by_author: DataLoader[int, int]
    post_by_id: DataLoader[int, list[Post]]
    comments_by_post: DataLoader[int, list[Comment]]
    comments_count_by_post: DataLoader[int, int]


async def load_posts_by_author(
    session: AsyncSession, author_ids: list[int]
) -> list[list[Post]]:
    posts = await PostRepository(session).list_by_authors(author_ids)
    grouped: dict[int, list[Post]] = {author_id: [] for author_id in author_ids}
    for post in posts:
        grouped[post.author_id].append(post)
    return [grouped[author_id] for author_id in author_ids]


async def load_post_by_id(
    session: AsyncSession, post_ids: list[int]
) -> list[list[Post]]:
    posts = await PostRepository(session).list_by_ids(post_ids)
    by_id = {post.id: post for post in posts}
    return [by_id[post_id] for post_id in post_ids]


async def load_posts_count_by_author(
    session: AsyncSession, author_ids: list[int]
) -> list[int]:
    posts_count = await PostRepository(session).count_by_authors(author_ids)
    return [posts_count.get(author_id, 0) for author_id in author_ids]


async def load_comments_by_post(
    session: AsyncSession, post_ids: list[int]
) -> list[list[Comment]]:
    comments = await CommentRepository(session).list_by_posts(post_ids)
    grouped: dict[int, list[Comment]] = {post_id: [] for post_id in post_ids}
    for comment in comments:
        grouped[comment.post_id].append(comment)
    return [grouped[post_id] for post_id in post_ids]


async def load_comments_count_by_post(
    session: AsyncSession, post_ids: list[int]
) -> list[int]:
    comments_count = await CommentRepository(session).count_by_posts(post_ids)
    return [comments_count.get(post_id, 0) for post_id in post_ids]


def create_blog_loaders(session: AsyncSession) -> BlogLoaders:
    return BlogLoaders(
        posts_by_author=DataLoader(load_fn=partial(load_posts_by_author, session)),
        posts_count_by_author=DataLoader(
            load_fn=partial(load_posts_count_by_author, session)
        ),
        post_by_id=DataLoader(load_fn=partial(load_post_by_id, session)),
        comments_by_post=DataLoader(load_fn=partial(load_comments_by_post, session)),
        comments_count_by_post=DataLoader(
            load_fn=partial(load_comments_count_by_post, session)
        ),
    )
