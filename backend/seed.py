"""
Seed script — populates Threadline with demo users, posts, comments, replies, and likes.

Usage:
    # Against production
    python seed.py --base-url https://threadline-backend.onrender.com

    # Against local dev
    python seed.py --base-url http://localhost:8000
"""

import argparse
import requests

# ---------------------------------------------------------------------------
# Demo data
# ---------------------------------------------------------------------------

USERS = [
    {"first_name": "Alice",   "last_name": "Chen",    "email": "alice@demo.com",   "password": "Demo1234!"},
    {"first_name": "Bob",     "last_name": "Rahman",  "email": "bob@demo.com",     "password": "Demo1234!"},
    {"first_name": "Clara",   "last_name": "Santos",  "email": "clara@demo.com",   "password": "Demo1234!"},
    {"first_name": "David",   "last_name": "Kim",     "email": "david@demo.com",   "password": "Demo1234!"},
    {"first_name": "Eva",     "last_name": "Müller",  "email": "eva@demo.com",     "password": "Demo1234!"},
]

POSTS = [
    {"user": "alice@demo.com",  "content": "Just launched my new portfolio! 🚀 Been working on it for months. Let me know what you think.", "visibility": "public"},
    {"user": "bob@demo.com",    "content": "Hot take: tabs are better than spaces and I'm tired of pretending otherwise.", "visibility": "public"},
    {"user": "clara@demo.com",  "content": "Had the best coffee this morning. Sometimes the small things matter the most. ☕", "visibility": "public"},
    {"user": "david@demo.com",  "content": "Just finished reading Atomic Habits. Highly recommend it to anyone trying to build better routines.", "visibility": "public"},
    {"user": "eva@demo.com",    "content": "Working from a café today. The background noise somehow makes me more productive. Anyone else like this?", "visibility": "public"},
    {"user": "alice@demo.com",  "content": "Three years into my dev journey and I still google how to center a div. Some things never change 😂", "visibility": "public"},
    {"user": "bob@demo.com",    "content": "PSA: Always back up your work before a big refactor. Learned this the hard way today.", "visibility": "public"},
    {"user": "clara@demo.com",  "content": "Started learning Spanish on Duolingo. Day 12 streak and going strong! 🇪🇸", "visibility": "public"},
    {"user": "david@demo.com",  "content": "Reminder that done is better than perfect. Ship it, iterate, improve.", "visibility": "public"},
    {"user": "eva@demo.com",    "content": "This is a private note to myself — need to review PR #42 before standup tomorrow.", "visibility": "private"},
    {"user": "alice@demo.com",  "content": "Open source contribution of the week: fixed a typo in the docs. It counts!", "visibility": "public"},
    {"user": "bob@demo.com",    "content": "React Query + FastAPI is such a great combo. Highly recommend this stack.", "visibility": "public"},
]

COMMENTS = [
    {"post_index": 0, "user": "bob@demo.com",   "content": "Looks amazing! The layout is really clean."},
    {"post_index": 0, "user": "clara@demo.com", "content": "Love the colour scheme! What did you use to build it?"},
    {"post_index": 1, "user": "alice@demo.com", "content": "Hard disagree 😅 but I respect the conviction."},
    {"post_index": 1, "user": "eva@demo.com",   "content": "The only correct answer is: whatever your team agrees on."},
    {"post_index": 3, "user": "clara@demo.com", "content": "Just added it to my reading list. Thanks for the recommendation!"},
    {"post_index": 5, "user": "david@demo.com", "content": "Every single time 😂 that's what documentation is for!"},
    {"post_index": 8, "user": "alice@demo.com", "content": "This is exactly what I needed to hear today. Thank you!"},
    {"post_index": 11, "user": "clara@demo.com", "content": "Been using this stack for 6 months now. Absolutely love it."},
]

REPLIES = [
    {"comment_index": 0, "user": "alice@demo.com", "content": "Thank you so much! I used Figma for the design then coded it from scratch."},
    {"comment_index": 1, "user": "alice@demo.com", "content": "Next.js! And all the CSS is handwritten — no Tailwind."},
    {"comment_index": 3, "user": "bob@demo.com",   "content": "Exactly! Consistency over ideology."},
]

# Posts that include an image — picsum.photos provides free placeholder images
# Each entry: (user, caption, picsum_image_id, visibility)
IMAGE_POSTS = [
    ("alice@demo.com",  "Beautiful morning view from my desk today 🌅",           "1015", "public"),
    ("bob@demo.com",    "Current reading stack. Any recommendations to add? 📚",   "24",   "public"),
    ("clara@demo.com",  "Cooked this for dinner last night. Turned out amazing! 🍝","292",  "public"),
    ("david@demo.com",  "Took a walk in the park this weekend. Needed the reset 🌿","15",   "public"),
    ("eva@demo.com",    "New desk setup is finally done. Minimal and clean 💻",     "338",  "public"),
    ("alice@demo.com",  "Captured this on my morning run. Nature is something else 🌸", "82", "public"),
]

LIKES = [
    # (post_index, user)
    (0, "bob@demo.com"), (0, "clara@demo.com"), (0, "david@demo.com"), (0, "eva@demo.com"),
    (1, "alice@demo.com"), (1, "clara@demo.com"),
    (2, "alice@demo.com"), (2, "bob@demo.com"), (2, "david@demo.com"),
    (3, "alice@demo.com"), (3, "eva@demo.com"),
    (5, "bob@demo.com"), (5, "david@demo.com"), (5, "eva@demo.com"),
    (8, "alice@demo.com"), (8, "bob@demo.com"), (8, "clara@demo.com"),
    (11, "alice@demo.com"), (11, "david@demo.com"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def register(base_url: str, user: dict) -> bool:
    r = requests.post(f"{base_url}/api/auth/register", json=user)
    if r.status_code == 201:
        print(f"  ✓ Registered {user['email']}")
        return True
    elif r.status_code == 400 and "already" in r.text.lower():
        print(f"  ~ Already exists: {user['email']}")
        return True
    else:
        print(f"  ✗ Failed to register {user['email']}: {r.text}")
        return False


def login(base_url: str, email: str, password: str) -> requests.Session | None:
    s = requests.Session()
    r = s.post(f"{base_url}/api/auth/login", json={"email": email, "password": password})
    if r.status_code == 200:
        return s
    print(f"  ✗ Login failed for {email}: {r.text}")
    return None


def create_post(session: requests.Session, base_url: str, content: str, visibility: str) -> dict | None:
    r = session.post(f"{base_url}/api/posts", data={"content": content, "visibility": visibility})
    if r.status_code == 201:
        return r.json()
    print(f"  ✗ Post failed: {r.text}")
    return None


def create_post_with_image(session: requests.Session, base_url: str, content: str, image_id: str, visibility: str) -> dict | None:
    try:
        img_response = requests.get(f"https://picsum.photos/id/{image_id}/800/600", timeout=15)
        img_response.raise_for_status()
    except Exception as e:
        print(f"  ✗ Image download failed (id={image_id}): {e}")
        return create_post(session, base_url, content, visibility)

    files = {"image": (f"photo_{image_id}.jpg", img_response.content, "image/jpeg")}
    data = {"content": content, "visibility": visibility}
    r = session.post(f"{base_url}/api/posts", data=data, files=files)
    if r.status_code == 201:
        return r.json()
    print(f"  ✗ Image post failed: {r.text}")
    return None


def create_comment(session: requests.Session, base_url: str, post_id: str, content: str) -> dict | None:
    r = session.post(f"{base_url}/api/comments/post/{post_id}", json={"content": content})
    if r.status_code == 201:
        return r.json()
    print(f"  ✗ Comment failed: {r.text}")
    return None


def create_reply(session: requests.Session, base_url: str, comment_id: str, content: str) -> dict | None:
    r = session.post(f"{base_url}/api/replies/comment/{comment_id}", json={"content": content})
    if r.status_code == 201:
        return r.json()
    print(f"  ✗ Reply failed: {r.text}")
    return None


def like_post(session: requests.Session, base_url: str, post_id: str):
    r = session.post(f"{base_url}/api/likes/post/{post_id}")
    if r.status_code not in (201, 400):
        print(f"  ✗ Like failed: {r.text}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    print(f"\nSeeding against: {base_url}\n")

    # 1. Register all users
    print("=== Registering users ===")
    for u in USERS:
        register(base_url, u)

    # 2. Log in all users
    print("\n=== Logging in ===")
    sessions: dict[str, requests.Session] = {}
    for u in USERS:
        s = login(base_url, u["email"], u["password"])
        if s:
            sessions[u["email"]] = s
            print(f"  ✓ Logged in {u['email']}")

    # 3. Create posts
    print("\n=== Creating posts ===")
    created_posts = []
    for p in POSTS:
        s = sessions.get(p["user"])
        if not s:
            created_posts.append(None)
            continue
        post = create_post(s, base_url, p["content"], p["visibility"])
        created_posts.append(post)
        if post:
            print(f"  ✓ Post by {p['user']}: \"{p['content'][:50]}...\"")

    # 4. Create comments
    print("\n=== Creating comments ===")
    created_comments = []
    for c in COMMENTS:
        post = created_posts[c["post_index"]] if c["post_index"] < len(created_posts) else None
        if not post:
            created_comments.append(None)
            continue
        s = sessions.get(c["user"])
        if not s:
            created_comments.append(None)
            continue
        comment = create_comment(s, base_url, post["id"], c["content"])
        created_comments.append(comment)
        if comment:
            print(f"  ✓ Comment by {c['user']}")

    # 5. Create replies
    print("\n=== Creating replies ===")
    for r in REPLIES:
        comment = created_comments[r["comment_index"]] if r["comment_index"] < len(created_comments) else None
        if not comment:
            continue
        s = sessions.get(r["user"])
        if not s:
            continue
        reply = create_reply(s, base_url, comment["id"], r["content"])
        if reply:
            print(f"  ✓ Reply by {r['user']}")

    # 6. Create image posts
    print("\n=== Creating image posts ===")
    for user_email, content, image_id, visibility in IMAGE_POSTS:
        s = sessions.get(user_email)
        if not s:
            continue
        post = create_post_with_image(s, base_url, content, image_id, visibility)
        if post:
            print(f"  ✓ Image post by {user_email} (picsum id={image_id})")

    # 7. Like posts
    print("\n=== Liking posts ===")
    for post_index, user_email in LIKES:
        post = created_posts[post_index] if post_index < len(created_posts) else None
        if not post:
            continue
        s = sessions.get(user_email)
        if not s:
            continue
        like_post(s, base_url, post["id"])
    print(f"  ✓ Applied {len(LIKES)} likes")

    print("\n✅ Seed complete!\n")
    print("Demo accounts (all passwords: Demo1234!):")
    for u in USERS:
        print(f"  {u['email']}")


if __name__ == "__main__":
    main()
