import SEO from "@/components/SEO";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

const Index = () => {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-subtle">
      <SEO title="Biblioteca | Shelf Sync Saga" description="Gestiona tu librería: catálogo de libros y control de usuarios. Login y CRUD con integración a OpenLibrary." canonical={
        window.location.origin + "/"
      } />
      <section className="container text-center space-y-6">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
          Tu Biblioteca, organizada al instante
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Inicia sesión y administra el catálogo: crea, lee, actualiza y elimina libros. Búsqueda por ISBN con datos de OpenLibrary.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Button asChild variant="hero" size="lg">
            <Link to="/login">Iniciar sesión</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link to="/books">Ver libros</Link>
          </Button>
        </div>
      </section>
    </main>
  );
};

export default Index;
