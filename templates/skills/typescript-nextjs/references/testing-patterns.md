# Next.js Testing Patterns Reference

## Testing Stack

| Tool | Purpose |
|---|---|
| **Vitest** (or Jest) | Unit and integration tests |
| **Testing Library** | Component rendering and assertions |
| **MSW** | API mocking (Mock Service Worker) |
| **Playwright** | End-to-end browser tests |

## Testing Server Components

Server Components cannot be tested with Testing Library directly (they're async and run on the server). Test them through:

### Integration Tests (API layer)

```tsx
// __tests__/api/users.test.ts
import { GET, POST } from "@/app/api/users/route";
import { NextRequest } from "next/server";

describe("GET /api/users", () => {
  it("returns users list", async () => {
    const request = new NextRequest("http://localhost/api/users");
    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.data).toBeInstanceOf(Array);
  });

  it("returns 401 without auth", async () => {
    // mock auth to return null
    vi.mocked(auth).mockResolvedValueOnce(null);
    const request = new NextRequest("http://localhost/api/users");
    const response = await GET(request);

    expect(response.status).toBe(401);
  });
});
```

### Testing Server Actions

```tsx
// __tests__/actions/posts.test.ts
import { createPost } from "@/app/posts/actions";

vi.mock("next/cache", () => ({
  revalidatePath: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  redirect: vi.fn(),
}));

describe("createPost", () => {
  it("creates a post and redirects", async () => {
    const formData = new FormData();
    formData.set("title", "Test Post");
    formData.set("content", "Content here");

    await createPost(formData);

    expect(redirect).toHaveBeenCalledWith(expect.stringContaining("/posts/"));
    expect(revalidatePath).toHaveBeenCalledWith("/posts");
  });
});
```

## Testing Client Components

```tsx
// __tests__/components/SearchFilter.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { SearchFilter } from "@/components/features/SearchFilter";

describe("SearchFilter", () => {
  it("calls onSearch when input changes", () => {
    const onSearch = vi.fn();
    render(<SearchFilter onSearch={onSearch} />);

    fireEvent.change(screen.getByPlaceholderText("Search..."), {
      target: { value: "test" },
    });

    expect(onSearch).toHaveBeenCalledWith("test");
  });

  it("displays current query value", () => {
    render(<SearchFilter onSearch={vi.fn()} />);
    const input = screen.getByPlaceholderText("Search...");

    fireEvent.change(input, { target: { value: "hello" } });

    expect(input).toHaveValue("hello");
  });
});
```

## MSW Setup for API Mocking

### Setup File

```tsx
// __tests__/mocks/handlers.ts
import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("/api/users", () => {
    return HttpResponse.json({
      data: [
        { id: "1", name: "Alice", email: "alice@example.com" },
        { id: "2", name: "Bob", email: "bob@example.com" },
      ],
    });
  }),

  http.post("/api/users", async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ data: { id: "3", ...body } }, { status: 201 });
  }),
];
```

```tsx
// __tests__/mocks/server.ts
import { setupServer } from "msw/node";
import { handlers } from "./handlers";

export const server = setupServer(...handlers);
```

```tsx
// vitest.setup.ts
import { server } from "./__tests__/mocks/server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Override Handlers in Tests

```tsx
import { server } from "../mocks/server";
import { http, HttpResponse } from "msw";

it("handles API error", async () => {
  server.use(
    http.get("/api/users", () => {
      return HttpResponse.json({ error: "Server Error" }, { status: 500 });
    }),
  );

  // Test error handling behavior
});
```

## E2E Tests with Playwright

```tsx
// e2e/auth.spec.ts
import { test, expect } from "@playwright/test";

test.describe("Authentication", () => {
  test("user can log in", async ({ page }) => {
    await page.goto("/login");
    await page.fill("[name=email]", "user@example.com");
    await page.fill("[name=password]", "password123");
    await page.click("button[type=submit]");

    await expect(page).toHaveURL("/dashboard");
    await expect(page.locator("h1")).toContainText("Dashboard");
  });

  test("shows error for invalid credentials", async ({ page }) => {
    await page.goto("/login");
    await page.fill("[name=email]", "wrong@example.com");
    await page.fill("[name=password]", "wrong");
    await page.click("button[type=submit]");

    await expect(page.locator("[role=alert]")).toContainText("Invalid credentials");
  });
});
```

### Playwright Page Object Pattern

```tsx
// e2e/pages/LoginPage.ts
import { Page, expect } from "@playwright/test";

export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto("/login");
  }

  async login(email: string, password: string) {
    await this.page.fill("[name=email]", email);
    await this.page.fill("[name=password]", password);
    await this.page.click("button[type=submit]");
  }

  async expectError(message: string) {
    await expect(this.page.locator("[role=alert]")).toContainText(message);
  }
}
```

## Testing Rules

| Rule | Reason |
|---|---|
| Test API routes as integration tests | They're the contract between client and server |
| Mock external APIs with MSW | Deterministic, network-independent |
| Test client components with Testing Library | Tests user behavior, not implementation |
| Use Playwright for critical user flows | E2E catches integration issues |
| Don't test Server Components with render() | They're async; test via API or E2E |
| Mock `next/cache` and `next/navigation` | They throw outside Next.js runtime |
| Test form validation both client and server | Never trust client-side only |
