from django.db.models import Count
from django.shortcuts import render
from blog.models import Comment, Post, Tag


def serialize_post(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_qty,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
        "first_tag_title": post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        "title": tag.title,
        "posts_with_tag": tag.posts_qty,
    }


def index(request):
    most_popular_posts = (
        Post.objects.get_popular_posts()
        .fetch_with_tags_posts_qty()
        .prefetch_related("author")[:5]
        .prefetch_related("tags")
        .fetch_with_comments_count()
    )

    fresh_posts = (
        Post.objects.order_by("-published_at")
        .annotate(comments_qty=Count("comments"))
        .fetch_with_tags_posts_qty()
        .prefetch_related("author")[:5]
        .prefetch_related("tags")
    )

    most_fresh_posts = fresh_posts
    most_popular_tags = Tag.objects.get_popular_posts()[:5]
    context = {
        "most_popular_posts": [
            serialize_post(post) for post in most_popular_posts
        ],
        "page_posts": [
            serialize_post(post) for post in most_fresh_posts
        ],
        "popular_tags": [
            serialize_tag(tag)
            for tag in most_popular_tags.annotate(
                posts_qty=Count("posts", distinct=True)
            )
        ],
    }
    return render(request, "index.html", context)


def post_detail(request, slug):
    post = (
        Post.objects.annotate(likes_amount=Count("comments"))
        .fetch_with_tags_posts_qty()
        .select_related("author")
        .get(slug=slug)
    )

    comments = (
        Comment.objects.filter(post=post).select_related("author").all()
    )
    serialized_comments = []
    for comment in comments:
        serialized_comments.append(
            {
                "text": comment.text,
                "published_at": comment.published_at,
                "author": comment.author.username,
            }
        )

    related_tags = post.tags.all()

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        "likes_amount": post.likes_amount,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.get_popular_posts()[:5]

    most_popular_posts = (
        Post.objects.get_popular_posts()
        .fetch_with_tags_posts_qty()
        .select_related("author")[:5]
        .fetch_with_comments_count()
    )

    context = {
        "post": serialized_post,
        "popular_tags": [
            serialize_tag(tag)
            for tag in most_popular_tags.annotate(
                posts_qty=Count("posts", distinct=True)
            )
        ],
        "most_popular_posts": [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, "post-details.html", context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)
    most_popular_tags = Tag.objects.get_popular_posts()[:5]

    most_popular_posts = (
        Post.objects.get_popular_posts()
        .fetch_with_tags_posts_qty()
        .prefetch_related("author")[:5]
        .fetch_with_comments_count()
    )
    related_posts = (
        tag.posts.prefetch_related("author")
        .fetch_with_tags_posts_qty()[:20]
        .fetch_with_comments_count()
    )

    context = {
        "tag": tag.title,
        "popular_tags": [
            serialize_tag(tag)
            for tag in most_popular_tags.annotate(
                posts_qty=Count("posts", distinct=True)
            )
        ],
        "posts": [serialize_post(post) for post in related_posts],
        "most_popular_posts": [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, "posts-list.html", context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, "contacts.html", {})
