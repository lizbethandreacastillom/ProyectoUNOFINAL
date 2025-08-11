import { useLocation } from "react-router-dom";
import { useEffect } from "react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-3">
        <h1 className="text-4xl font-bold">404</h1>
        <p className="text-xl text-muted-foreground">¡Ups! Página no encontrada</p>
        <a href="/" className="underline text-primary hover:opacity-90">Volver al inicio</a>
      </div>
    </main>
  );
};

export default NotFound;
