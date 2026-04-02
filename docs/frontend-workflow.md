# Frontend Workflow

This document explains how data flows through the Next.js frontend — from the server rendering a page to a user clicking "Like" and seeing the count change instantly.

---

## Application Bootstrap

When the browser first loads `/feed`, three layers of logic run in sequence:

```
1. Edge Middleware (src/middleware.ts)
   ↓ checks access_token cookie
   ↓ redirects to /login if missing (before any HTML is rendered)

2. Server Component (src/app/feed/page.tsx)
   ↓ reads cookies() from next/headers
   ↓ secondary check — redirects if cookie missing
   ↓ renders the page shell (Navbar, sidebars, layout)

3. Client Components (PostFeed, CreatePostBox, etc.)
   ↓ mount in the browser
   ↓ AuthContext.useEffect → GET /api/auth/me → populates user state
   ↓ React Query → GET /api/posts → populates feed
```

The two-layer route protection (middleware + server component) ensures that even if the cookie check at the edge has a bug, the server component acts as a safety net before any sensitive HTML is sent.

---

## Authentication State (AuthContext)

`src/context/AuthContext.tsx` is a React Context that holds the current `user` object globally.

```typescript
interface AuthContextValue {
  user: User | null;   // null = not logged in
  loading: boolean;    // true while /api/auth/me is in-flight
  setUser: (u: User | null) => void;
}
```

**On mount:** The `AuthProvider` calls `GET /api/auth/me`. If the access token is valid, the user is populated. If not, `user` stays `null`.

**On login/register:** The form components call `setUser(res.data)` immediately after a successful API call — no page refresh needed.

**On logout:** `setUser(null)` then `router.push('/login')`.

**Why not localStorage?** Tokens in localStorage are accessible to JavaScript, making them vulnerable to XSS attacks. httpOnly cookies cannot be read by JavaScript — they are sent automatically by the browser and are invisible to any script, including injected malicious scripts.

---

## Silent Token Refresh (Axios Interceptor)

`src/lib/api.ts` wraps Axios with a response interceptor:

```typescript
api.interceptors.response.use(
  (response) => response,      // pass through successful responses
  async (error) => {
    const detail = error.response?.data?.detail;

    // Only intercept "token_expired" 401, not other auth errors
    if (error.response?.status === 401 && detail === "token_expired" && !original._retry) {
      original._retry = true;

      // POST /api/auth/refresh sends the refresh_token cookie automatically
      await axios.post("/api/auth/refresh", {}, { withCredentials: true });

      // Retry the original failed request — now with the new access_token cookie
      return api(original);
    }

    return Promise.reject(error);
  }
);
```

**Queue handling:** If multiple requests fail at the same time (e.g., the feed and a comment load fire simultaneously and both get 401), the interceptor uses a queue. Only one refresh request is sent; all queued requests retry after it completes. This prevents the "refresh storm" problem.

```typescript
let isRefreshing = false;
let failedQueue: Array<{ resolve, reject }> = [];
// if already refreshing → push to queue instead of sending another refresh
```

**From the user's perspective:** The token expires silently. They never see a login prompt during normal use unless the refresh token itself expires (after 7 days of inactivity).

---

## Data Fetching (React Query)

React Query manages all server state. It handles caching, deduplication, and background refetching.

### Feed (Infinite Query)

```typescript
// hooks/usePosts.ts
useInfiniteQuery({
  queryKey: ["posts"],
  queryFn: ({ pageParam }) => api.get(`/api/posts?cursor=${pageParam}`),
  getNextPageParam: (lastPage) => lastPage.at(-1)?.created_at,
})
```

`data.pages` is an array of pages: `[[post1, post2, ...], [post11, post12, ...], ...]`.
`PostFeed` calls `data.pages.flat()` to render all posts in one list.

### Optimistic Like Update

When a user clicks Like, the UI updates **immediately** before the API call completes:

```typescript
// PostCard.tsx
async function toggleLike() {
  const prev = liked;
  setLiked(!prev);                          // ← instant UI update
  setLikeCount((c) => c + (prev ? -1 : 1));  // ← instant count change

  try {
    const res = await api.post(`/api/likes/post/${post.id}`);
    setLikeCount(res.data.like_count);      // sync with server truth
  } catch {
    setLiked(prev);                         // revert on failure
    setLikeCount((c) => c + (prev ? 1 : -1));
  }
}
```

If the network call fails (e.g., the user is briefly offline), the UI reverts to the previous state. The user gets instant feedback with automatic error recovery.

### Cache Update on New Post

When a post is created, the new post is **prepended to the React Query cache** without refetching the entire feed:

```typescript
// hooks/usePosts.ts — useCreatePost mutation
onSuccess: (newPost) => {
  queryClient.setQueryData(["posts"], (old) => ({
    ...old,
    pages: [[newPost, ...old.pages[0]], ...old.pages.slice(1)],
  }));
}
```

This means the user sees their new post at the top of the feed instantly, and no network request is made to reload the feed.

---

## Component Hierarchy

```
feed/page.tsx  (Server Component)
├── DarkModeToggle  (Client — toggles ._dark_wrapper class)
├── Navbar          (Client — profile dropdown, logout)
├── LeftSidebar     (Server — static JSX)
├── RightSidebar    (Server — static JSX)
├── StoriesCarousel (Server — static JSX)
├── CreatePostBox   (Client — controlled form, FormData submit)
└── PostFeed        (Client — infinite query)
    └── PostCard[]  (Client — like toggle, comment toggle)
        ├── CommentSection  (Client — shown on "Comment" click)
        │   └── CommentItem[]
        │       └── ReplyItem[]
        └── WhoLikedModal   (Client — shown on like count click)
```

**Server Components** (Navbar wrapper, sidebars, page shell) render on the server and send pure HTML — no JavaScript hydration needed for static content.

**Client Components** (marked `"use client"`) require interactivity and are hydrated in the browser. They are as leaf-level as possible to minimize JavaScript bundle size.

---

## Request Flow: Creating a Post

```
User types text, picks image, clicks "Post"
      │
CreatePostBox.handleSubmit()
      │
FormData { content, visibility, image }
      │
api.post('/api/posts', formData, { 'Content-Type': 'multipart/form-data' })
      │
Axios → Next.js rewrite → FastAPI POST /api/posts
      │                         │
      │                    validate image type/size
      │                    save UUID-named file to /app/static/uploads/
      │                    INSERT into posts
      │                    return PostResponse JSON
      │
onSuccess callback
      │
queryClient.setQueryData(['posts'], prepend newPost to page[0])
      │
React re-renders PostFeed → new post appears at top
```

No page reload. No full feed refetch. The new post appears at the top within ~200ms of clicking "Post" (including the network round-trip).

---

## Dark Mode

`DarkModeToggle.tsx` replicates the original `custom.js` behavior:

```javascript
// original custom.js
document.querySelector('._layout_swithing_btn_link').addEventListener('click', function() {
  document.querySelector('._layout').classList.toggle('_dark_wrapper');
});
```

```typescript
// DarkModeToggle.tsx
function toggle() {
  const el = document.querySelector("._layout");
  el?.classList.toggle("_dark_wrapper", !dark);
  document.body.classList.toggle("_dark_body", !dark);
}
```

The `_dark_wrapper` class is defined in the original `main.css` and switches all colours using CSS custom properties — no Tailwind, no CSS-in-JS, just the original design system.
