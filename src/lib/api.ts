export type Book = {
  id: string;
  title: string;
  author: string;
  isbn: string;
  stock: number;
  category: string;
};

export type User = {
  id: string;
  email: string;
};

const BOOKS_KEY = "books_data";
const USERS_KEY = "users_data";
const TOKEN_KEY = "auth_token";

function ensureSeed() {
  // Seed default user and some books
  if (!localStorage.getItem(USERS_KEY)) {
    localStorage.setItem(
      USERS_KEY,
      JSON.stringify([{ id: crypto.randomUUID(), email: "admin@example.com", password: "admin123" }])
    );
  }
  if (!localStorage.getItem(BOOKS_KEY)) {
    localStorage.setItem(
      BOOKS_KEY,
      JSON.stringify([
        { id: crypto.randomUUID(), title: "El Quijote", author: "Miguel de Cervantes", isbn: "9788420412147", stock: 3, category: "Clásico" },
        { id: crypto.randomUUID(), title: "Cien años de soledad", author: "G. G. Márquez", isbn: "9780307474728", stock: 5, category: "Novela" },
      ])
    );
  }
}

ensureSeed();

function delay<T>(data: T, ms = 300): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(data), ms));
}

export async function login(email: string, password: string): Promise<User> {
  const users = JSON.parse(localStorage.getItem(USERS_KEY) || "[]");
  const found = users.find((u: any) => u.email === email && u.password === password);
  if (!found) throw new Error("Credenciales inválidas");
  const token = crypto.randomUUID();
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem("current_user", JSON.stringify({ id: found.id, email: found.email }));
  return delay({ id: found.id, email: found.email });
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem("current_user");
}

export function getCurrentUser(): User | null {
  const raw = localStorage.getItem("current_user");
  return raw ? JSON.parse(raw) : null;
}

export async function getBooks(): Promise<Book[]> {
  const data: Book[] = JSON.parse(localStorage.getItem(BOOKS_KEY) || "[]");
  return delay(data);
}

export async function createBook(input: Omit<Book, "id"> | Book): Promise<Book> {
  const data: Book[] = JSON.parse(localStorage.getItem(BOOKS_KEY) || "[]");
  const book: Book = { ...(input as Book), id: crypto.randomUUID() };
  localStorage.setItem(BOOKS_KEY, JSON.stringify([book, ...data]));
  return delay(book);
}

export async function updateBook(id: string, input: Partial<Book>): Promise<Book> {
  const data: Book[] = JSON.parse(localStorage.getItem(BOOKS_KEY) || "[]");
  const idx = data.findIndex((b) => b.id === id);
  if (idx === -1) throw new Error("No encontrado");
  const updated = { ...data[idx], ...input, id } as Book;
  data[idx] = updated;
  localStorage.setItem(BOOKS_KEY, JSON.stringify(data));
  return delay(updated);
}

export async function deleteBook(id: string): Promise<void> {
  const data: Book[] = JSON.parse(localStorage.getItem(BOOKS_KEY) || "[]");
  const next = data.filter((b) => b.id !== id);
  localStorage.setItem(BOOKS_KEY, JSON.stringify(next));
  return delay(undefined);
}

export async function fetchBookByISBN(isbn: string): Promise<{ title?: string; author?: string }> {
  // External API: OpenLibrary
  const res = await fetch(`https://openlibrary.org/isbn/${encodeURIComponent(isbn)}.json`);
  if (!res.ok) throw new Error("ISBN no encontrado");
  const json = await res.json();
  const title = json.title as string | undefined;
  let author: string | undefined;
  try {
    if (Array.isArray(json.authors) && json.authors[0]?.key) {
      const authorsRes = await fetch(`https://openlibrary.org${json.authors[0].key}.json`);
      const a = await authorsRes.json();
      author = a.name;
    }
  } catch {
    // ignore
  }
  return { title, author };
}
