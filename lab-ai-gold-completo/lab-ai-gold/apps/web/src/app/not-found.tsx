import Link from "next/link";
export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center text-center px-4">
      <div>
        <div className="text-6xl mb-4">⬡</div>
        <h1 className="text-4xl font-bold text-gold-gradient mb-2">404</h1>
        <p className="text-neutral-400 mb-6">Página não encontrada</p>
        <Link href="/dashboard" className="btn-gold">Voltar ao painel</Link>
      </div>
    </div>
  );
}
