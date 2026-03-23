# Next.js Data Fetching Patterns Reference

## Server Component Data Fetching

### Basic Pattern

```tsx
// app/products/page.tsx
export default async function ProductsPage() {
  const products = await getProducts();
  return <ProductList products={products} />;
}

async function getProducts() {
  const res = await fetch("https://api.example.com/products", {
    next: { revalidate: 3600 }, // ISR: revalidate every hour
  });
  if (!res.ok) throw new Error("Failed to fetch products");
  return res.json() as Promise<Product[]>;
}
```

### Caching Strategies

| Strategy | How | When |
|---|---|---|
| **Static** | `fetch(url)` (default cached) | Rarely changing data |
| **ISR** | `fetch(url, { next: { revalidate: N } })` | Data changes periodically |
| **Dynamic** | `fetch(url, { cache: "no-store" })` | Always fresh data |
| **On-demand** | `revalidateTag("products")` or `revalidatePath("/products")` | After mutations |

### Tag-Based Revalidation

```tsx
// Fetch with tags
async function getProducts() {
  const res = await fetch("https://api.example.com/products", {
    next: { tags: ["products"] },
  });
  return res.json();
}

// Server Action: revalidate on mutation
"use server";
import { revalidateTag } from "next/cache";

export async function createProduct(data: ProductInput) {
  await db.insert(products).values(data);
  revalidateTag("products"); // Invalidate all fetches tagged "products"
}
```

## Parallel Data Loading

### Avoid Waterfalls

```tsx
// BAD: Sequential (waterfall)
export default async function DashboardPage() {
  const user = await getUser();      // 200ms
  const orders = await getOrders();  // 300ms
  const stats = await getStats();    // 150ms
  // Total: 650ms
}

// GOOD: Parallel
export default async function DashboardPage() {
  const [user, orders, stats] = await Promise.all([
    getUser(),     // 200ms
    getOrders(),   // 300ms
    getStats(),    // 150ms
  ]);
  // Total: 300ms (longest)
}
```

### Streaming with Suspense

```tsx
import { Suspense } from "react";

export default async function DashboardPage() {
  const user = await getUser(); // Fast, needed for layout

  return (
    <div>
      <UserHeader user={user} />
      <Suspense fallback={<OrdersSkeleton />}>
        <OrdersSection /> {/* Streams in when ready */}
      </Suspense>
      <Suspense fallback={<StatsSkeleton />}>
        <StatsSection /> {/* Streams in independently */}
      </Suspense>
    </div>
  );
}

// Each section fetches its own data
async function OrdersSection() {
  const orders = await getOrders(); // Slow query
  return <OrderList orders={orders} />;
}
```

## Direct Database Access

With ORMs like Drizzle or Prisma, skip the API layer entirely in Server Components:

```tsx
// app/users/page.tsx
import { db } from "@/lib/db";
import { users } from "@/lib/schema";

export default async function UsersPage() {
  const allUsers = await db.select().from(users).limit(50);
  return <UserTable users={allUsers} />;
}
```

## Server Actions for Mutations

### Form Actions

```tsx
// app/posts/new/page.tsx
import { createPost } from "./actions";

export default function NewPostPage() {
  return (
    <form action={createPost}>
      <input name="title" required />
      <textarea name="content" required />
      <button type="submit">Create Post</button>
    </form>
  );
}
```

```tsx
// app/posts/new/actions.ts
"use server";

import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";

export async function createPost(formData: FormData) {
  const title = formData.get("title") as string;
  const content = formData.get("content") as string;

  const post = await db.insert(posts).values({ title, content }).returning();
  revalidatePath("/posts");
  redirect(`/posts/${post[0].id}`);
}
```

### Programmatic Server Actions

```tsx
"use client";

import { useTransition } from "react";
import { deletePost } from "./actions";

export function DeleteButton({ postId }: { postId: string }) {
  const [isPending, startTransition] = useTransition();

  return (
    <button
      disabled={isPending}
      onClick={() => startTransition(() => deletePost(postId))}
    >
      {isPending ? "Deleting..." : "Delete"}
    </button>
  );
}
```

## Error Handling

### Error Boundaries

```tsx
// app/dashboard/error.tsx
"use client";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

### Loading States

```tsx
// app/dashboard/loading.tsx
export default function DashboardLoading() {
  return <DashboardSkeleton />;
}
```

### Not Found

```tsx
// In a Server Component
import { notFound } from "next/navigation";

export default async function UserPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const user = await getUser(id);
  if (!user) notFound();
  return <UserProfile user={user} />;
}
```

## Data Fetching Rules

| Rule | Reason |
|---|---|
| Fetch in Server Components, not `useEffect` | Faster, no client-server waterfall |
| Use `Promise.all` for independent fetches | Avoid sequential waterfalls |
| Use Suspense for non-critical data | Stream content progressively |
| Set `revalidate` or `cache` on every fetch | Be explicit about caching intent |
| Use `revalidateTag` after mutations | Precise cache invalidation |
| Access DB directly in Server Components | Skip unnecessary API roundtrips |
| Validate all Server Action inputs | Server Actions are public endpoints |
