"""
Gerador de relatório PDF — LAB AI GOLD.
Usa ReportLab para gerar PDF em memória.
Retorna bytes prontos para download.
"""
from __future__ import annotations

import io
from datetime import datetime, timezone
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ─── Cores da marca ───────────────────────────────────────────────────────────
GOLD   = colors.HexColor("#f59e0b")
DARK   = colors.HexColor("#111111")
GRAY   = colors.HexColor("#404040")
LIGHT  = colors.HexColor("#f5f5f5")
RED    = colors.HexColor("#ef4444")
YELLOW = colors.HexColor("#eab308")
GREEN  = colors.HexColor("#22c55e")

PRIORITY_COLORS = {"high": RED, "medium": YELLOW, "low": GREEN}
PRIORITY_LABELS = {"high": "Alta", "medium": "Média", "low": "Baixa"}


def generate_report_pdf(
    project_name: str,
    project_description: str | None,
    area_ha: float | None,
    analysis: dict[str, Any],
    points: list[dict[str, Any]],
    user_name: str,
) -> bytes:
    """
    Gera e retorna o PDF do relatório de análise em bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title=f"LAB AI GOLD — {project_name}",
        author="LAB AI GOLD",
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph(
        "<font color='#f59e0b'><b>⬡ LAB AI GOLD</b></font>",
        ParagraphStyle("brand", fontSize=22, textColor=GOLD, spaceAfter=4, alignment=TA_LEFT),
    ))
    story.append(Paragraph(
        "Relatório de Análise Geoespacial",
        ParagraphStyle("subtitle", fontSize=11, textColor=GRAY, spaceAfter=2),
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=14))

    # ── Info do projeto ───────────────────────────────────────────────────────
    story.append(Paragraph(
        f"<b>{project_name}</b>",
        ParagraphStyle("projname", fontSize=16, textColor=DARK, spaceAfter=4),
    ))
    if project_description:
        story.append(Paragraph(project_description,
            ParagraphStyle("desc", fontSize=10, textColor=GRAY, spaceAfter=8)))

    meta = [
        ["Área total",        f"{area_ha:.1f} ha" if area_ha else "—"],
        ["Algoritmo",         analysis.get("algorithm", "v1").upper()],
        ["Fatores analisados",", ".join(analysis.get("factors_used", []))],
        ["Solicitado por",    user_name],
        ["Data do relatório", datetime.now(tz=timezone.utc).strftime("%d/%m/%Y %H:%M UTC")],
    ]
    meta_table = Table(meta, colWidths=[5 * cm, 11 * cm])
    meta_table.setStyle(TableStyle([
        ("FONTSIZE",  (0,0), (-1,-1), 9),
        ("TEXTCOLOR", (0,0), (0,-1), GRAY),
        ("TEXTCOLOR", (1,0), (1,-1), DARK),
        ("FONTNAME",  (0,0), (0,-1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [LIGHT, colors.white]),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 16))

    # ── Resumo de distribuição ────────────────────────────────────────────────
    story.append(Paragraph(
        "<b>Distribuição dos Pontos Prioritários</b>",
        ParagraphStyle("sec", fontSize=12, textColor=DARK, spaceAfter=8),
    ))

    summary = analysis.get("summary_json") or analysis
    dist_data = [
        ["Prioridade", "Pontos", "Critério"],
        ["🔴 Alta",    str(summary.get("high",   3)), "Score ≥ 68%"],
        ["🟡 Média",   str(summary.get("medium", 4)), "Score 45–67%"],
        ["🟢 Baixa",   str(summary.get("low",    3)), "Score < 45%"],
    ]
    dist_table = Table(dist_data, colWidths=[6*cm, 3*cm, 7*cm])
    dist_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0),  DARK),
        ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
        ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT, colors.white]),
        ("ALIGN",       (1,0), (1,-1),  "CENTER"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    story.append(dist_table)
    story.append(Spacer(1, 20))

    # ── Pontos ────────────────────────────────────────────────────────────────
    story.append(Paragraph(
        "<b>Detalhamento dos 10 Pontos</b>",
        ParagraphStyle("sec", fontSize=12, textColor=DARK, spaceAfter=8),
    ))

    sorted_pts = sorted(points, key=lambda p: p.get("rank", 99))
    for pt in sorted_pts:
        prio   = pt.get("priority", "low")
        pct    = int(pt.get("score", 0) * 100)
        color  = PRIORITY_COLORS.get(prio, GREEN)
        plabel = PRIORITY_LABELS.get(prio, prio)

        # Cabeçalho do ponto
        pt_header = Table(
            [[f"{pt.get('label','?')}  —  {plabel} prioridade", f"Score: {pct}%"]],
            colWidths=[12*cm, 4*cm]
        )
        pt_header.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), color),
            ("TEXTCOLOR",     (0,0), (-1,-1), colors.white),
            ("FONTNAME",      (0,0), (-1,-1), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
            ("LEFTPADDING",   (0,0), (0,-1),  8),
            ("ALIGN",         (1,0), (1,-1),  "RIGHT"),
            ("RIGHTPADDING",  (1,0), (1,-1),  8),
        ]))
        story.append(pt_header)

        # Coordenadas
        story.append(Paragraph(
            f"<font size=8 color='#666'>📍 {pt.get('lat',0):.5f}, {pt.get('lng',0):.5f}</font>",
            ParagraphStyle("coord", leftIndent=8, spaceAfter=4, spaceBefore=4),
        ))

        # Justificativas
        reasons = pt.get("reasons_json", [])
        for r in reasons:
            story.append(Paragraph(
                f"◆  {r}",
                ParagraphStyle("reason", fontSize=9, textColor=GRAY,
                               leftIndent=12, spaceAfter=2, spaceBefore=1),
            ))

        story.append(Spacer(1, 10))

    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY, spaceBefore=4, spaceAfter=10))

    # ── Aviso legal ───────────────────────────────────────────────────────────
    story.append(Paragraph(
        "<b>⚠️ Aviso Importante</b>",
        ParagraphStyle("warn_title", fontSize=10, textColor=YELLOW, spaceAfter=4),
    ))
    story.append(Paragraph(
        "Os resultados apresentados neste relatório são <b>estimativas probabilísticas</b> "
        "geradas por análise de dados de sensoriamento remoto e modelos computacionais. "
        "Eles NÃO garantem, sob nenhuma circunstância, a presença de ouro ou outros minerais "
        "na área analisada. Sempre consulte um geólogo licenciado antes de iniciar qualquer "
        "atividade de exploração mineral.",
        ParagraphStyle("warn", fontSize=8, textColor=GRAY, leading=12),
    ))

    doc.build(story)
    return buffer.getvalue()
