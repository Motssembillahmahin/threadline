# From Static HTML/CSS/JS to Next.js

This document explains how the three original static HTML pages (`login.html`, `registration.html`, `feed.html`) were converted into a working Next.js application without changing a single CSS class or visual style.

---

## The Design Constraint

The original files form a complete design system:

```
assets/
  css/
    bootstrap.min.css   ← Bootstrap 5 grid + utilities
    common.css          ← CSS variables, resets, shared tokens
    main.css            ← 140KB of component-specific styles
    responsive.css      ← Breakpoint overrides
  js/
    bootstrap.bundle.min.js
    custom.js           ← 55 lines: dark mode toggle + dropdown handlers
  images/               ← 103 files (PNG, SVG)
  fonts/                ← FontAwesome + Flaticon
```

**Rule:** Every class name in the original HTML must appear unchanged in the React component. No Tailwind, no CSS Modules, no renaming. The visual output must be pixel-identical to the static files.

---

## Step 1: Preserve the Assets

The entire `assets/` folder was copied verbatim to `frontend/public/assets/`. In Next.js, files in `public/` are served at the root URL path.

| Original path | Next.js URL |
|---|---|
| `assets/css/main.css` | `/assets/css/main.css` |
| `assets/images/logo.svg` | `/assets/images/logo.svg` |
| `assets/fonts/flaticon.woff2` | `/assets/fonts/flaticon.woff2` |

---

## Step 2: Import All CSS Globally

Original HTML files each had four `<link>` tags. In Next.js, CSS is imported once in the root layout.

**Original (repeated in every HTML file):**
```html
<link rel="stylesheet" href="assets/css/bootstrap.min.css">
<link rel="stylesheet" href="assets/css/common.css">
<link rel="stylesheet" href="assets/css/main.css">
<link rel="stylesheet" href="assets/css/responsive.css">
```

**Next.js (`src/app/globals.css`):**
```css
@import url('/assets/css/bootstrap.min.css');
@import url('/assets/css/common.css');
@import url('/assets/css/main.css');
@import url('/assets/css/responsive.css');
```

`globals.css` is imported in `src/app/layout.tsx`, which wraps every page. The result is identical — all four stylesheets load on every page.

---

## Step 3: Fonts

Original HTML loaded the Poppins font in a `<link>` tag inside `<head>`. Next.js `layout.tsx` has a `<head>` section where the same link tags are placed.

**Original:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@100;300;400;500;600;700;800&display=swap" rel="stylesheet">
```

**Next.js (`layout.tsx`):**
```tsx
<head>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@100..." rel="stylesheet" />
</head>
```

Note: JSX uses `crossOrigin` (camelCase) where HTML uses `crossorigin`. This is a React requirement — HTML attribute names become camelCase props.

---

## Step 4: Converting HTML Structure to JSX

The most mechanical part of the conversion. Every HTML element becomes a JSX element, with two key rules:

| HTML | JSX | Reason |
|---|---|---|
| `class="..."` | `className="..."` | `class` is a reserved JS keyword |
| `crossorigin="anonymous"` | `crossOrigin="anonymous"` | Event attributes are camelCase in React |
| `for="inputId"` | `htmlFor="inputId"` | `for` is a reserved JS keyword |
| `<input>` | `<input />` | JSX requires self-closing tags |
| `<img src="...">` | `<img src="..." />` | Same — JSX self-closing |
| `href="feed.html"` | `href="/feed"` | Next.js routes don't have `.html` extensions |

### Example: Login form

**Original HTML:**
```html
<form class="_social_login_form">
  <div class="_social_login_form_input _mar_b14">
    <label class="_social_login_label _mar_b8">Email</label>
    <input type="email" class="form-control _social_login_input">
  </div>
  <div class="_social_login_form_btn _mar_t40 _mar_b60">
    <button type="button" class="_social_login_form_btn_link _btn1">Login now</button>
  </div>
</form>
```

**JSX (`LoginForm.tsx`):**
```tsx
<form className="_social_login_form" onSubmit={handleSubmit}>
  <div className="_social_login_form_input _mar_b14">
    <label className="_social_login_label _mar_b8">Email</label>
    <input
      type="email"
      className="form-control _social_login_input"
      value={email}
      onChange={(e) => setEmail(e.target.value)}
      required
    />
  </div>
  <div className="_social_login_form_btn _mar_t40 _mar_b60">
    <button type="submit" className="_social_login_form_btn_link _btn1" disabled={loading}>
      {loading ? "Logging in..." : "Login now"}
    </button>
  </div>
</form>
```

Every original class name is unchanged. The only additions are React event handlers (`onSubmit`, `onChange`), controlled input state (`value`, `onChange`), and a loading state for the button — all of which are invisible to CSS.

---

## Step 5: Navigation — `<a href>` to `<Link>`

Original HTML used plain anchor tags for navigation:
```html
<a href="feed.html">Home</a>
<a href="login.html">Login</a>
```

In Next.js, `<Link>` from `next/link` is used for client-side navigation (no full page reload):
```tsx
import Link from "next/link";

<Link href="/feed">Home</Link>
<Link href="/login">Login</Link>
```

`<Link>` renders as an `<a>` tag in the final HTML, so all CSS rules targeting `a` still apply. To the browser and to the CSS, it looks identical.

---

## Step 6: Images — `<img>` vs `next/image`

The project uses plain `<img>` tags for two reasons:

1. All images are in `public/assets/` — served as static files, no optimisation needed
2. Post images need a dynamic URL pattern that `next/image` handles via `remotePatterns`

For post images from the API, `next/image` would require the backend domain to be whitelisted in `next.config.ts`:

```typescript
// next.config.ts
images: {
  remotePatterns: [
    { protocol: "http", hostname: "localhost", port: "8000", pathname: "/static/uploads/**" },
    { protocol: "http", hostname: "backend", port: "8000", pathname: "/static/uploads/**" },
  ],
}
```

The two hostnames are needed because:
- `localhost:8000` is used in the browser (client-side rendering)
- `backend:8000` is the Docker service name (server-side rendering inside the container network)

---

## Step 7: JavaScript Behaviour → React State

The original `custom.js` had two behaviours:
1. Dark mode toggle — adds `_dark_wrapper` class to `.layout`
2. Dropdown visibility — shows/hides elements

**Original JavaScript:**
```javascript
// custom.js
document.querySelector('._layout_swithing_btn_link').addEventListener('click', function() {
  document.querySelector('._layout').classList.toggle('_dark_wrapper');
});

document.getElementById('_profile_drop_show_btn').addEventListener('click', function() {
  document.getElementById('_prfoile_drop').classList.toggle('_show');
});
```

**React equivalent:**
```tsx
// DarkModeToggle.tsx
const [dark, setDark] = useState(false);
function toggle() {
  document.querySelector("._layout")?.classList.toggle("_dark_wrapper", !dark);
  setDark(!dark);
}
```

```tsx
// Navbar.tsx
const [dropdownOpen, setDropdownOpen] = useState(false);
// ...
{dropdownOpen && <div className="_nav_profile_dropdown">...</div>}
```

React's conditional rendering (`{condition && <element />}`) replaces the CSS class toggling for show/hide. The dark mode case keeps the DOM class manipulation because the `_dark_wrapper` class must be on the actual DOM element for the CSS to apply — React state alone cannot affect CSS class-based theming without touching the DOM.

---

## Step 8: Route Structure

| Original file | Next.js route | Notes |
|---|---|---|
| `login.html` | `/login` → `app/(auth)/login/page.tsx` | Route group `(auth)` doesn't affect the URL |
| `registration.html` | `/register` → `app/(auth)/register/page.tsx` | |
| `feed.html` | `/feed` → `app/feed/page.tsx` | Protected route |
| — | `/` → `app/page.tsx` | Redirects to `/feed` |

The `(auth)` route group is a Next.js App Router feature. The parentheses mean the folder name is ignored in the URL — `/login` not `/(auth)/login`. It's used purely for file organisation.

---

## What Changed vs What Didn't

### Unchanged
- Every CSS class name from the original HTML
- All four CSS files, loaded in the same order
- All images and fonts
- The visual layout at every breakpoint
- The Bootstrap grid (`col-xl-3`, `col-xl-6`, etc.)
- Dark mode behaviour

### Changed (minimal, necessary)
- `class` → `className` (JSX syntax requirement)
- `href="feed.html"` → `href="/feed"` (Next.js routing)
- Static button `onclick` → React `onClick` with `useState`
- Static `<form>` → controlled form with `onSubmit` + API call
- Hardcoded user names → dynamic data from API
- Static post images → `<img src={apiBaseUrl + post.image_url} />`
- Navigation added: Register form has first/last name fields (missing from original, required by the task spec)

### Added (new UI, no original equivalent)
- Error messages on login/register forms
- Loading states on buttons
- "Load more" button in the feed
- Post visibility selector (Public/Private) in CreatePostBox
- Comment/reply textarea inputs
- WhoLikedModal (click like count to see who liked)
