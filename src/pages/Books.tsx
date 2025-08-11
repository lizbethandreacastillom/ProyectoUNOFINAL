import SEO from "@/components/SEO";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useEffect, useMemo, useState } from "react";
import { Book, createBook, deleteBook, fetchBookByISBN, getBooks, getCurrentUser, logout, updateBook } from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import { Link, useNavigate } from "react-router-dom";

const empty: Book = { id: "", title: "", author: "", isbn: "", stock: 0, category: "" };

const Books = () => {
  const [form, setForm] = useState<Book>(empty);
  const [items, setItems] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const user = useMemo(() => getCurrentUser(), []);

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    (async () => {
      const data = await getBooks();
      setItems(data);
      setLoading(false);
    })();
  }, [navigate, user]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (form.id) {
        const updated = await updateBook(form.id, form);
        setItems((prev) => prev.map((b) => (b.id === updated.id ? updated : b)));
        toast({ title: "Libro actualizado" });
      } else {
        const created = await createBook(form);
        setItems((prev) => [created, ...prev]);
        toast({ title: "Libro creado" });
      }
      setForm(empty);
    } catch (e: any) {
      toast({ title: "Error", description: e?.message || "Intenta de nuevo" });
    }
  };

  const onEdit = (book: Book) => setForm(book);
  const onDelete = async (id: string) => {
    await deleteBook(id);
    setItems((prev) => prev.filter((b) => b.id !== id));
    toast({ title: "Libro eliminado" });
  };

  const onISBNLookup = async () => {
    if (!form.isbn) return;
    try {
      const info = await fetchBookByISBN(form.isbn);
      setForm((f) => ({ ...f, title: info.title || f.title, author: info.author || f.author }));
      toast({ title: "Datos obtenidos", description: "Completamos título/autor desde OpenLibrary" });
    } catch {
      toast({ title: "ISBN no encontrado", description: "Verifica el número" });
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <main className="min-h-screen pb-16">
      <SEO title="Libros | Biblioteca" description="Tabla y formulario CRUD de libros." canonical={window.location.origin + "/books"} />

      <header className="container flex items-center justify-between py-6">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold">Catálogo de libros</h1>
          <p className="text-sm text-muted-foreground">Administra tu inventario</p>
        </div>
        <div className="flex items-center gap-2">
          <Button asChild variant="outline"><Link to="/">Inicio</Link></Button>
          <Button variant="secondary" onClick={handleLogout}>Salir</Button>
        </div>
      </header>

      <section className="container grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>{form.id ? "Editar libro" : "Nuevo libro"}</CardTitle>
            <CardDescription>Completa los campos para {form.id ? "actualizar" : "crear"}</CardDescription>
          </CardHeader>
          <CardContent>
            <form className="grid grid-cols-1 md:grid-cols-2 gap-4" onSubmit={onSubmit}>
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="isbn">ISBN</Label>
                <div className="flex gap-2">
                  <Input id="isbn" value={form.isbn} onChange={(e) => setForm({ ...form, isbn: e.target.value })} placeholder="978..." />
                  <Button type="button" variant="soft" onClick={onISBNLookup}>Buscar</Button>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="title">Título</Label>
                <Input id="title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="author">Autor</Label>
                <Input id="author" value={form.author} onChange={(e) => setForm({ ...form, author: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="category">Categoría</Label>
                <Input id="category" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="stock">Stock</Label>
                <Input id="stock" type="number" value={form.stock} onChange={(e) => setForm({ ...form, stock: Number(e.target.value) })} />
              </div>
              <div className="md:col-span-2 flex gap-2">
                <Button type="submit" variant="hero">{form.id ? "Guardar cambios" : "Crear libro"}</Button>
                {form.id && (
                  <Button type="button" variant="ghost" onClick={() => setForm(empty)}>Cancelar</Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Listado</CardTitle>
            <CardDescription>{loading ? "Cargando..." : `${items.length} libro(s) en catálogo`}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Título</TableHead>
                    <TableHead>Autor</TableHead>
                    <TableHead>ISBN</TableHead>
                    <TableHead>Categoría</TableHead>
                    <TableHead className="text-right">Stock</TableHead>
                    <TableHead className="text-right">Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((b) => (
                    <TableRow key={b.id}>
                      <TableCell>{b.title}</TableCell>
                      <TableCell>{b.author}</TableCell>
                      <TableCell>{b.isbn}</TableCell>
                      <TableCell>{b.category}</TableCell>
                      <TableCell className="text-right">{b.stock}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button size="sm" variant="outline" onClick={() => onEdit(b)}>Editar</Button>
                          <Button size="sm" variant="destructive" onClick={() => onDelete(b.id)}>Eliminar</Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                  {!items.length && !loading && (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center text-muted-foreground">Sin resultados</TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </section>
    </main>
  );
};

export default Books;
