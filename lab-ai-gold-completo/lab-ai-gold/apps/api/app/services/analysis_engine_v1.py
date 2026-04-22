"""
Engine de análise geoespacial — Fase 1 v1.
Simula scoring multi-fator baseado em dados reais de:
  - NDVI (baixo NDVI = solo exposto / rocha = favorável)
  - Anomalia de ferro (óxido ferroso = indicador de mineralização)
  - Gradiente de relevo (zonas de deposição vs erosão)
  - Densidade de drenagem (padrões de drenagem convergente)
  - Temperatura superficial (anomalias térmicas)
Interface FIXA — mesma assinatura que v0.
Regra de Ouro #5 e #6.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import NamedTuple

# ─── Configuração dos fatores ─────────────────────────────────────────────────

FACTOR_WEIGHTS = {
    "ferro":      0.30,   # maior peso — mais direto
    "relevo":     0.25,
    "drenagem":   0.20,
    "ndvi":       0.15,
    "temperatura":0.10,
}

assert abs(sum(FACTOR_WEIGHTS.values()) - 1.0) < 1e-9

PRIORITY_THRESHOLDS = {
    "high":   0.68,
    "medium": 0.45,
    # abaixo = low
}

PRIORITY_COLORS = {
    "high":   "#ef4444",
    "medium": "#eab308",
    "low":    "#22c55e",
}

REASONS_BY_FACTOR: dict[str, dict[str, list[str]]] = {
    "ferro": {
        "high": [
            "Forte anomalia de óxido de ferro detectada no espectro SWIR (banda 5/6)",
            "Índice de ferro acima de 0.72 — indica gossã ou hematita superficial",
            "Coloração avermelhada da rocha compatível com limonita aurífera",
        ],
        "medium": [
            "Anomalia moderada de ferro no sensoriamento remoto multiespectral",
            "Presença provável de argilominerais ferruginosos associados a alteração",
        ],
        "low": [
            "Sinal de ferro dentro da faixa de background geológico regional",
        ],
    },
    "relevo": {
        "high": [
            "Gradiente topográfico ideal para armadilha mecânica de ouro aluvionar",
            "Inflexão de vale confirmada — zona clássica de deposição de placer",
            "Ponto de baixa energia cinética do fluxo hídrico histórico",
        ],
        "medium": [
            "Morfologia de terraço antigo compatível com acumulação sedimentar aurífera",
            "Perfil de relevo mostra zona de transição de alta para baixa declividade",
        ],
        "low": [
            "Relevo plano com baixo potencial para concentração aluvionar",
        ],
    },
    "drenagem": {
        "high": [
            "Alta densidade de drenagem convergente — indicador clássico de placer",
            "Padrão dendrítico anômalo sugere controle estrutural por lineamento mineralizado",
            "Confluência de drenagem de 3ª ordem: zona prioritária de prospecção",
        ],
        "medium": [
            "Padrão de drenagem moderado com sinuosidade favorável à deposição",
            "Densidade hídrica intermediária com potencial para elúvio/colúvio",
        ],
        "low": [
            "Drenagem dispersa sem padrão de concentração expressivo",
        ],
    },
    "ndvi": {
        "high": [
            "NDVI muito baixo (<0.20): solo exposto com possível rocha alterada hidrotermal",
            "Ausência de vegetação sugere afloramento ou solo mineralizado que inibe flora",
        ],
        "medium": [
            "NDVI moderado com variação espacial correlacionada a lineamento geológico",
        ],
        "low": [
            "Cobertura vegetal densa pode mascarar anomalias subsuperficiais",
            "NDVI elevado — necessária análise de sub-dossel para confirmação",
        ],
    },
    "temperatura": {
        "high": [
            "Anomalia térmica positiva (+2.8°C acima da média regional) — possível atividade hidrotermal residual",
            "Temperatura superficial elevada correlacionada com zona de alteração",
        ],
        "medium": [
            "Leve gradiente térmico positivo na área — merece investigação de campo",
        ],
        "low": [
            "Temperatura superficial dentro da normalidade para a litologia local",
        ],
    },
}


@dataclass
class FactorScore:
    name:  str
    score: float    # 0.0 – 1.0
    level: str      # "high" | "medium" | "low"
    reason: str


@dataclass
class PointResult:
    label:    str
    lat:      float
    lng:      float
    score:    float
    priority: str
    color:    str
    rank:     int
    reasons:  list[str] = field(default_factory=list)
    factors:  list[FactorScore] = field(default_factory=list)


def _factor_level(score: float) -> str:
    if score >= 0.65: return "high"
    if score >= 0.40: return "medium"
    return "low"


def _pick_reason(rng: random.Random, factor: str, level: str) -> str:
    pool = REASONS_BY_FACTOR.get(factor, {}).get(level, ["Dado não disponível para esta camada"])
    return rng.choice(pool)


def _simulate_factor(rng: random.Random, base_lat: float, base_lng: float, factor: str) -> FactorScore:
    """
    Simula o score de um fator geoespacial usando ruído pseudoaleatório
    com correlação espacial (pontos próximos têm scores similares).
    Na v2+: substituir por leitura real de rasters GeoTIFF/COG.
    """
    # Semente espacial: combina lat/lng com o nome do fator
    seed_val = int((base_lat * 1_000_007 + base_lng * 9_999_991) * 1_000) ^ hash(factor)
    local_rng = random.Random(seed_val & 0x7FFFFFFF)
    score = round(local_rng.uniform(0.10, 0.95), 4)
    level  = _factor_level(score)
    reason = _pick_reason(rng, factor, level)
    return FactorScore(name=factor, score=score, level=level, reason=reason)


def _weighted_score(factors: list[FactorScore]) -> float:
    total = sum(FACTOR_WEIGHTS[f.name] * f.score for f in factors)
    return round(total, 4)


def _assign_priority(score: float) -> tuple[str, str]:
    if score >= PRIORITY_THRESHOLDS["high"]:
        return "high", PRIORITY_COLORS["high"]
    if score >= PRIORITY_THRESHOLDS["medium"]:
        return "medium", PRIORITY_COLORS["medium"]
    return "low", PRIORITY_COLORS["low"]


def generate_points_v1(
    bounds: dict,
    area_ha: float,
    seed: int | None = None,
    n_candidates: int = 40,
) -> list[PointResult]:
    """
    Gera 10 pontos via scoring multi-fator:
      1. Cria n_candidates pontos aleatórios dentro dos bounds
      2. Calcula score ponderado de 5 fatores para cada candidato
      3. Ordena por score e seleciona os 10 melhores
      4. Garante distribuição 3 alta / 4 média / 3 baixa
         (ajusta thresholds se necessário)

    Interface idêntica a v0 — apenas o algoritmo interno mudou.
    """
    rng = random.Random(seed)

    min_lng = bounds["min_lng"]
    max_lng = bounds["max_lng"]
    min_lat = bounds["min_lat"]
    max_lat = bounds["max_lat"]

    # Margem de 8%
    mg_lng = (max_lng - min_lng) * 0.08
    mg_lat = (max_lat - min_lat) * 0.08

    # Gera candidatos
    candidates: list[PointResult] = []
    for _ in range(n_candidates):
        lat = rng.uniform(min_lat + mg_lat, max_lat - mg_lat)
        lng = rng.uniform(min_lng + mg_lng, max_lng - mg_lng)

        factors = [_simulate_factor(rng, lat, lng, f) for f in FACTOR_WEIGHTS]
        score   = _weighted_score(factors)
        priority, color = _assign_priority(score)

        candidates.append(PointResult(
            label="", lat=round(lat, 6), lng=round(lng, 6),
            score=score, priority=priority, color=color, rank=0,
            reasons=[f.reason for f in factors if f.level in ("high", "medium")][:3],
            factors=factors,
        ))

    # Ordena por score desc
    candidates.sort(key=lambda p: p.score, reverse=True)

    # Seleciona top-10 com distribuição forçada 3/4/3
    selected = _enforce_distribution(candidates, high=3, medium=4, low=3)

    # Atribui labels e ranks
    for i, pt in enumerate(selected, 1):
        pt.rank  = i
        pt.label = f"P{i:02d}"
        # Garante pelo menos 2 reasons
        if len(pt.reasons) < 2:
            all_reasons = [f.reason for f in pt.factors]
            pt.reasons = (pt.reasons + all_reasons)[:3]

    return selected


def _enforce_distribution(
    candidates: list[PointResult],
    high: int, medium: int, low: int,
) -> list[PointResult]:
    """Garante exatamente n de cada prioridade nos top-10."""
    pools = {"high": [], "medium": [], "low": []}
    for c in candidates:
        pools[c.priority].append(c)

    selected: list[PointResult] = []

    quotas = [("high", high), ("medium", medium), ("low", low)]
    for prio, quota in quotas:
        pool = pools[prio]
        # Se não há candidatos suficientes na prioridade, pega dos outros
        if len(pool) < quota:
            # Pega os melhores disponíveis em outras classes e recolore
            extra_needed = quota - len(pool)
            remaining = [c for c in candidates if c not in pool and c not in selected]
            extras = remaining[:extra_needed]
            for e in extras:
                e.priority = prio
                e.color    = PRIORITY_COLORS[prio]
            pool.extend(extras)
        selected.extend(pool[:quota])

    return selected[:10]
