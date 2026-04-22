import Link from "next/link";

// ─── Ícones inline (sem dependência extra no Sprint 0) ────────────────────────
function IconMap() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round"
      className="w-6 h-6">
      <polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21" />
      <line x1="9" y1="3" x2="9" y2="18" /><line x1="15" y1="6" x2="15" y2="21" />
    </svg>
  );
}

function IconUpload() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round"
      className="w-6 h-6">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  );
}

function IconTarget() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round"
      className="w-6 h-6">
      <circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" />
      <circle cx="12" cy="12" r="2" />
    </svg>
  );
}

function IconShield() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round"
      className="w-6 h-6">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}

// ─── Dados estáticos ──────────────────────────────────────────────────────────
const features = [
  {
    icon: <IconUpload />,
    title: "Upload KML/KMZ",
    desc:  "Envie sua área de interesse diretamente da plataforma. Suporte a arquivos KML e KMZ com validação automática no servidor.",
  },
  {
    icon: <IconMap />,
    title: "Mapa Interativo",
    desc:  "Visualize sua área e os pontos prioritários em um mapa de alta resolução com zoom, rotação e camadas customizáveis.",
  },
  {
    icon: <IconTarget />,
    title: "10 Pontos Prioritários",
    desc:  "O engine geoespacial seleciona os 10 melhores pontos (3 alta · 4 média · 3 baixa prioridade) com justificativas detalhadas.",
  },
  {
    icon: <IconShield />,
    title: "Análise Probabilística",
    desc:  "Resultados baseados em dados reais de NDVI, ferro, relevo, drenagem e temperatura. Sem promessas, só probabilidades.",
  },
];

const steps = [
  { n: "01", label: "Crie seu projeto",       desc: "Cadastre-se e crie um projeto com nome e descrição da área." },
  { n: "02", label: "Faça upload da área",    desc: "Envie o arquivo KML ou KMZ delimitando a região de prospecção." },
  { n: "03", label: "Execute a análise",       desc: "Acione o engine. Em instantes o processamento geoespacial começa." },
  { n: "04", label: "Veja os resultados",     desc: "Receba os 10 pontos no mapa com scores, cores e justificativas." },
];

// ─── Componentes ──────────────────────────────────────────────────────────────
function PriorityBadge({ color, label, count }: { color: string; label: string; count: number }) {
  const styles: Record<string, string> = {
    red:    "bg-red-500/20 text-red-400 border-red-500/40",
    yellow: "bg-yellow-500/20 text-yellow-400 border-yellow-500/40",
    green:  "bg-green-500/20 text-green-400 border-green-500/40",
  };
  return (
    <div className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${styles[color]}`}>
      <span className={`w-2.5 h-2.5 rounded-full ${
        color === "red" ? "bg-red-400" : color === "yellow" ? "bg-yellow-400" : "bg-green-400"
      }`} />
      <span className="text-sm font-medium">{count} pontos</span>
      <span className="text-xs opacity-70">· {label}</span>
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────
export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">

      {/* ── Navbar ──────────────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-50 border-b border-dark-600 bg-dark-900/80 backdrop-blur-md">
        <div className="mx-auto max-w-7xl px-6 h-16 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gold-gradient flex items-center justify-center shadow-lg"
                 style={{ boxShadow: "0 0 16px rgba(245,158,11,0.4)" }}>
              <span className="text-dark-900 font-bold text-sm">⬡</span>
            </div>
            <span className="font-bold text-lg tracking-tight text-gold-gradient">LAB AI GOLD</span>
          </div>

          {/* Nav links */}
          <nav className="hidden md:flex items-center gap-6 text-sm text-neutral-400">
            <a href="#como-funciona" className="hover:text-gold-400 transition-colors">Como funciona</a>
            <a href="#funcionalidades" className="hover:text-gold-400 transition-colors">Funcionalidades</a>
          </nav>

          {/* CTA */}
          <div className="flex items-center gap-3">
            <Link href="/auth/login" className="btn-outline text-sm px-4 py-2">
              Entrar
            </Link>
            <Link href="/auth/register" className="btn-gold text-sm px-4 py-2">
              Começar grátis
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">

        {/* ── Hero ────────────────────────────────────────────────────────────── */}
        <section className="relative overflow-hidden py-24 md:py-36">
          {/* Background glow */}
          <div className="absolute inset-0 pointer-events-none" aria-hidden>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
                            w-[800px] h-[500px] rounded-full opacity-10"
                 style={{ background: "radial-gradient(ellipse, #f59e0b 0%, transparent 70%)" }} />
          </div>

          <div className="relative mx-auto max-w-4xl px-6 text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full
                            border border-gold-700/50 bg-gold-900/20 text-gold-400 text-xs font-medium mb-8">
              <span className="w-1.5 h-1.5 rounded-full bg-gold-400 animate-pulse" />
              Plataforma em desenvolvimento ativo · Sprint 0
            </div>

            {/* Título */}
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-tight">
              Prospecção de ouro{" "}
              <span className="text-gold-gradient">guiada por IA</span>
            </h1>

            <p className="text-lg md:text-xl text-neutral-400 max-w-2xl mx-auto mb-10 leading-relaxed">
              Faça upload da sua área de interesse em KML ou KMZ e receba os{" "}
              <strong className="text-neutral-200">10 pontos prioritários</strong> para prospecção,
              com scores probabilísticos e justificativas geoespaciais detalhadas.
            </p>

            {/* Priority badges */}
            <div className="flex flex-wrap justify-center gap-3 mb-12">
              <PriorityBadge color="red"    label="Alta prioridade"  count={3} />
              <PriorityBadge color="yellow" label="Média prioridade" count={4} />
              <PriorityBadge color="green"  label="Baixa prioridade" count={3} />
            </div>

            {/* CTAs */}
            <div className="flex flex-wrap justify-center gap-4">
              <Link href="/auth/register" className="btn-gold px-8 py-3 text-base font-semibold">
                Criar conta gratuita
              </Link>
              <a href="#como-funciona" className="btn-outline px-8 py-3 text-base">
                Ver como funciona
              </a>
            </div>
          </div>
        </section>

        {/* ── Mock do mapa ────────────────────────────────────────────────────── */}
        <section className="py-16 px-6">
          <div className="mx-auto max-w-5xl">
            <div className="relative rounded-2xl border border-dark-500 overflow-hidden shadow-2xl"
                 style={{ boxShadow: "0 0 60px rgba(245,158,11,0.08)" }}>
              {/* Header da janela */}
              <div className="flex items-center gap-2 px-4 py-3 bg-dark-700 border-b border-dark-500">
                <div className="w-3 h-3 rounded-full bg-red-500/60" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
                <div className="w-3 h-3 rounded-full bg-green-500/60" />
                <span className="ml-3 text-xs text-neutral-500 font-mono">
                  Projeto: Serra Dourada · 10 pontos analisados
                </span>
              </div>
              {/* Mapa placeholder */}
              <div className="h-80 bg-dark-800 relative flex items-center justify-center"
                   style={{
                     backgroundImage: `
                       linear-gradient(rgba(245,158,11,0.03) 1px, transparent 1px),
                       linear-gradient(90deg, rgba(245,158,11,0.03) 1px, transparent 1px)`,
                     backgroundSize: "40px 40px",
                   }}>
                <div className="text-center">
                  <div className="text-5xl mb-4">🗺️</div>
                  <p className="text-neutral-500 text-sm">
                    Mapa interativo disponível no Sprint 2
                  </p>
                  <p className="text-neutral-600 text-xs mt-1">
                    MapLibre GL · KML/KMZ · Pontos coloridos
                  </p>
                </div>
                {/* Pontos simulados */}
                {[
                  { top: "25%", left: "30%", color: "bg-red-500",    ring: "ring-red-500/40"    },
                  { top: "40%", left: "55%", color: "bg-red-500",    ring: "ring-red-500/40"    },
                  { top: "60%", left: "25%", color: "bg-red-500",    ring: "ring-red-500/40"    },
                  { top: "30%", left: "65%", color: "bg-yellow-500", ring: "ring-yellow-500/40" },
                  { top: "55%", left: "70%", color: "bg-yellow-500", ring: "ring-yellow-500/40" },
                  { top: "70%", left: "45%", color: "bg-yellow-500", ring: "ring-yellow-500/40" },
                  { top: "20%", left: "80%", color: "bg-yellow-500", ring: "ring-yellow-500/40" },
                  { top: "75%", left: "60%", color: "bg-green-500",  ring: "ring-green-500/40"  },
                  { top: "45%", left: "15%", color: "bg-green-500",  ring: "ring-green-500/40"  },
                  { top: "65%", left: "80%", color: "bg-green-500",  ring: "ring-green-500/40"  },
                ].map((p, i) => (
                  <div key={i}
                    className={`absolute w-3.5 h-3.5 rounded-full ${p.color} ring-2 ${p.ring}
                                shadow-lg animate-pulse-slow`}
                    style={{ top: p.top, left: p.left, animationDelay: `${i * 0.3}s` }} />
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ── Como funciona ───────────────────────────────────────────────────── */}
        <section id="como-funciona" className="py-24 px-6">
          <div className="mx-auto max-w-5xl">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Como <span className="text-gold-gradient">funciona</span>
              </h2>
              <p className="text-neutral-400 max-w-xl mx-auto">
                Do upload ao resultado em poucos minutos, tudo no navegador.
              </p>
            </div>
            <div className="grid md:grid-cols-4 gap-6">
              {steps.map((s) => (
                <div key={s.n} className="card relative group hover:border-gold-700/50 transition-colors">
                  <div className="text-3xl font-bold text-gold-800 mb-3 font-mono">{s.n}</div>
                  <h3 className="font-semibold text-neutral-100 mb-2">{s.label}</h3>
                  <p className="text-sm text-neutral-400 leading-relaxed">{s.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Funcionalidades ─────────────────────────────────────────────────── */}
        <section id="funcionalidades" className="py-24 px-6 border-t border-dark-600">
          <div className="mx-auto max-w-5xl">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Funcionalidades <span className="text-gold-gradient">principais</span>
              </h2>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              {features.map((f) => (
                <div key={f.title}
                     className="card flex gap-4 hover:border-gold-700/40 transition-colors group">
                  <div className="flex-shrink-0 w-11 h-11 rounded-lg bg-gold-500/10
                                  border border-gold-500/20 flex items-center justify-center
                                  text-gold-400 group-hover:bg-gold-500/20 transition-colors">
                    {f.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-neutral-100 mb-1">{f.title}</h3>
                    <p className="text-sm text-neutral-400 leading-relaxed">{f.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Aviso legal ────────────────────────────────────────────────────── */}
        <section className="py-12 px-6">
          <div className="mx-auto max-w-3xl">
            <div className="card border-yellow-700/30 bg-yellow-900/10 text-center">
              <p className="text-xs text-yellow-500/80 leading-relaxed">
                ⚠️ <strong className="text-yellow-400">Aviso importante:</strong>{" "}
                Os resultados fornecidos pelo LAB AI GOLD são <em>estimativas probabilísticas</em> baseadas
                em dados geoespaciais disponíveis e não garantem, sob nenhuma circunstância, a presença
                de ouro ou outros minerais na área analisada. Consulte sempre um geólogo licenciado antes
                de tomar decisões de exploração.
              </p>
            </div>
          </div>
        </section>

      </main>

      {/* ── Footer ──────────────────────────────────────────────────────────── */}
      <footer className="border-t border-dark-600 py-8 px-6">
        <div className="mx-auto max-w-7xl flex flex-col md:flex-row items-center
                        justify-between gap-4 text-sm text-neutral-500">
          <div className="flex items-center gap-2">
            <span className="text-gold-600">⬡</span>
            <span className="font-semibold text-neutral-400">LAB AI GOLD</span>
            <span>· Análise geoespacial probabilística</span>
          </div>
          <p>© {new Date().getFullYear()} LAB AI GOLD · Todos os direitos reservados</p>
        </div>
      </footer>

    </div>
  );
}
