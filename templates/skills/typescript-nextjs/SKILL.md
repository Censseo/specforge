---
name: typescript-nextjs
description: |
  Next.js App Router implementation patterns - server components, API routes, data fetching, state management, and testing.
  Activate when: implementing Next.js features, working with React server components, App Router, or Next.js API routes.
triggers: ["nextjs", "next.js", "app router", "server component", "react server", "next api"]
---

# Next.js App Router Patterns

> Best practices and conventions for Next.js 14+ with App Router and TypeScript.

## Project Structure

```
src/
├── app/
│   ├── layout.tsx            # Root layout (HTML shell)
│   ├── page.tsx              # Home page
│   ├── loading.tsx           # Root loading state
│   ├── error.tsx             # Root error boundary
│   ├── not-found.tsx         # 404 page
│   ├── (auth)/               # Route group (no URL segment)
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── dashboard/
│   │   ├── layout.tsx        # Dashboard layout (sidebar, etc.)
│   │   ├── page.tsx          # Dashboard home
│   │   └── settings/page.tsx
│   └── api/
│       └── users/
│           └── route.ts      # API route handler
├── components/
│   ├── ui/                   # Generic UI components (Button, Card, etc.)
│   └── features/             # Feature-specific components
├── lib/
│   ├── db.ts                 # Database client
│   ├── auth.ts               # Auth utilities
│   └── utils.ts              # Shared utilities
├── types/
│   └── index.ts              # Shared TypeScript types
└── middleware.ts              # Edge middleware (auth, redirects)
```

## Server vs Client Components

### Server Components (Default)

Every component in `app/` is a Server Component by default. Use for:
- Data fetching
- Accessing backend resources (DB, file system)
- Keeping sensitive data on server (API keys, tokens)
- Reducing client bundle size

```tsx
// app/dashboard/page.tsx — Server Component (no "use client")
import { db } from "@/lib/db";

export default async function DashboardPage() {
  const stats = await db.query.stats.findMany();

  return (
    <div>
      <h1>Dashboard</h1>
      <StatsList stats={stats} />
    </div>
  );
}
```

### Client Components

Add `"use client"` only when you need:
- Event handlers (onClick, onChange)
- State (useState, useReducer)
- Effects (useEffect)
- Browser APIs (window, localStorage)
- Third-party libraries that use React context

```tsx
"use client";

import { useState } from "react";

export function SearchFilter({ onSearch }: { onSearch: (q: string) => void }) {
  const [query, setQuery] = useState("");

  return (
    <input
      value={query}
      onChange={(e) => {
        setQuery(e.target.value);
        onSearch(e.target.value);
      }}
      placeholder="Search..."
    />
  );
}
```

### Composition Pattern

Keep Server Components as parents, push `"use client"` to leaf components:

```tsx
// Server Component (page.tsx)
export default async function ProductsPage() {
  const products = await getProducts(); // Server-side fetch

  return (
    <div>
      <SearchFilter onSearch={handleSearch} />  {/* Client */}
      <ProductList products={products} />         {/* Server */}
    </div>
  );
}
```

## API Routes (Route Handlers)

```tsx
// app/api/users/route.ts
import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db";
import { auth } from "@/lib/auth";

export async function GET(request: NextRequest) {
  const session = await auth();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const searchParams = request.nextUrl.searchParams;
  const page = parseInt(searchParams.get("page") ?? "1");
  const limit = Math.min(parseInt(searchParams.get("limit") ?? "20"), 100);

  const users = await db.query.users.findMany({
    limit,
    offset: (page - 1) * limit,
  });

  return NextResponse.json({ data: users, page, limit });
}

export async function POST(request: NextRequest) {
  const session = await auth();
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await request.json();
  // Validate with zod
  const parsed = createUserSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 });
  }

  const user = await db.insert(users).values(parsed.data).returning();
  return NextResponse.json({ data: user }, { status: 201 });
}
```

### Dynamic Route Parameters

```tsx
// app/api/users/[id]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const user = await db.query.users.findFirst({ where: eq(users.id, id) });
  if (!user) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }
  return NextResponse.json({ data: user });
}
```

## Data Fetching

### Server Component Fetch

```tsx
// Fetch with revalidation
async function getProducts() {
  const res = await fetch("https://api.example.com/products", {
    next: { revalidate: 3600 }, // Revalidate every hour
  });
  if (!res.ok) throw new Error("Failed to fetch");
  return res.json();
}

// No caching (always fresh)
async function getCurrentUser() {
  const res = await fetch("https://api.example.com/me", {
    cache: "no-store",
  });
  return res.json();
}
```

### Server Actions

```tsx
// app/actions.ts
"use server";

import { revalidatePath } from "next/cache";

export async function createPost(formData: FormData) {
  const title = formData.get("title") as string;
  const content = formData.get("content") as string;

  await db.insert(posts).values({ title, content });
  revalidatePath("/posts");
}
```

## Middleware

```tsx
// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("session")?.value;

  // Protect dashboard routes
  if (request.nextUrl.pathname.startsWith("/dashboard") && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/api/:path*"],
};
```

## Input Validation (Zod)

```tsx
import { z } from "zod";

export const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(100),
  role: z.enum(["user", "admin"]).default("user"),
});

export type CreateUserInput = z.infer<typeof createUserSchema>;
```

## Security Checklist

- [ ] Use middleware for auth checks on protected routes
- [ ] Validate all inputs with Zod in API routes and Server Actions
- [ ] Never expose server-only env vars to client (prefix with `NEXT_PUBLIC_` only for public vars)
- [ ] Use `httpOnly` cookies for session tokens (not localStorage)
- [ ] Set security headers in `next.config.js` (CSP, HSTS, X-Frame-Options)
- [ ] Rate limit API routes (use middleware or edge functions)
- [ ] Sanitize user-generated HTML before rendering

## Common Anti-Patterns

| Anti-Pattern | Better Approach |
|---|---|
| `"use client"` on every component | Default to Server Components, push interactivity to leaves |
| Fetching in `useEffect` | Fetch in Server Components or use Server Actions |
| Large client bundles | Use dynamic imports: `const Chart = dynamic(() => import("./Chart"))` |
| Waterfall data fetching | Fetch in parallel: `const [a, b] = await Promise.all([...])` |
| Prop drilling through layouts | Use Server Components + direct DB access at each level |
| Client-side auth checks only | Use middleware for route protection |
| Hardcoded API URLs | Use environment variables |

## Quick Reference

| Aspect | Convention |
|--------|-----------|
| **Components** | Server by default, `"use client"` only when needed |
| **Data fetching** | Server Components or Server Actions |
| **Validation** | Zod schemas for all inputs |
| **Auth** | Middleware for routes, `auth()` in Server Components/Actions |
| **State** | Server state via fetch, client state via Zustand/Jotai |
| **Styling** | Tailwind CSS or CSS Modules |
| **API routes** | `app/api/` with NextRequest/NextResponse |
| **Testing** | Vitest + Testing Library + MSW + Playwright |
