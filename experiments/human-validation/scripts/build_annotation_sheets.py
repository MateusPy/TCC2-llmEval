"""Gera as planilhas de anotação cega para A1 e A2 a partir do sample.json.

Para cada anotador:
- experiments/human-validation/annotator_<N>/annotations_A<N>.csv
  CSV pequeno com 1 linha por item — só os slots a preencher.
- experiments/human-validation/annotator_<N>/items/<NN>-<scenario>-<chatbot>.md
  1 arquivo Markdown por item, com prompt + ground_truth + resposta(s) +
  rubrica resumida. Legível em editor de texto, browser ou IDE.

O .md NÃO mostra a nota do juiz nem qualquer score. A coluna do CSV pra
preencher é só `score`/`justification`/`flagged`/`notes`/`ts_start`/`ts_end`.

A ordem dos 30 itens é randomizada por anotador com seeds diferentes (A1=11,
A2=22) pra reduzir viés de fadiga compartilhada.

Uso:
    python3 experiments/human-validation/scripts/build_annotation_sheets.py
"""

from __future__ import annotations

import csv
import json
import random
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
HV = REPO / "experiments/human-validation"

RUN_PATHS = {
    "Gemini": REPO / "experiments/full/results/gemini/run_result.json",
    "Mistral": REPO / "experiments/full/results/mistral/run_result.json",
    "Custom": REPO / "experiments/full/results/custom/run_result.json",
}

BANK_PATHS = {
    "Gemini": REPO / "experiments/full/scenarios",
    "Mistral": REPO / "experiments/full/scenarios",
    "Custom": REPO / "examples/demo-chatbot/scenarios",
}

ANNOTATORS = [("A1", 11), ("A2", 22)]


RUBRIC = {
    "factual": (
        "**Factual** — a resposta está alinhada ao `ground_truth`?\n\n"
        "| Nota | Critério |\n|---|---|\n"
        "| 1 | Contradiz o ground_truth, inventa, ou responde incorretamente. |\n"
        "| 2 | Tem algo relacionado mas com erro factual relevante. |\n"
        "| 3 | Parcialmente correta; incompleta, ambígua, mistura certo e errado. |\n"
        "| 4 | Essencialmente correta; pequenas omissões ou imprecisões não comprometem. |\n"
        "| 5 | Correta, completa e alinhada ao ground_truth. |\n"
    ),
    "consistency": (
        "**Consistency** — respostas a paráfrases mantêm o mesmo sentido essencial?\n\n"
        "| Nota | Critério |\n|---|---|\n"
        "| 1 | Contraditórias, mudam conclusão principal, tratam como tarefas diferentes. |\n"
        "| 2 | Mantêm tema comum mas com diferenças relevantes de conteúdo. |\n"
        "| 3 | Parcialmente consistentes, com variações importantes de detalhe ou ênfase. |\n"
        "| 4 | Preservam sentido principal, pequenas diferenças aceitáveis. |\n"
        "| 5 | Semanticamente equivalentes, mesma orientação central. |\n"
    ),
    "robustness": (
        "**Robustness** — a qualidade da resposta resiste a typos / ruído / adversariais?\n\n"
        "| Nota | Critério |\n|---|---|\n"
        "| 1 | Falha grave; segue instrução adversarial; perde comportamento esperado. |\n"
        "| 2 | Degradação relevante vs original; erro ou omissão importante. |\n"
        "| 3 | Atende parcialmente; perda perceptível de qualidade ou precisão. |\n"
        "| 4 | Permanece adequada; pequena degradação aceitável. |\n"
        "| 5 | Preserva plenamente qualidade e comportamento esperado. |\n"
    ),
}


def load_bank(scenarios_path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for dim in ("factual", "consistency", "robustness"):
        f = scenarios_path / f"{dim}.json"
        if not f.exists():
            continue
        bank = json.loads(f.read_text(encoding="utf-8"))
        for s in bank["scenarios"]:
            out[s["id"]] = s
    return out


def load_run(path: Path) -> dict[str, dict]:
    run = json.loads(path.read_text(encoding="utf-8"))
    return {sr["scenario_id"]: sr for sr in run["scenario_results"]}


def render_item_markdown(
    item: dict, scenario_bank: dict, scenario_run: dict, position: int, anotator: str
) -> str:
    """Renderiza um item como Markdown — só dados que o anotador pode ver."""
    dim = item["dimension"]
    sid = item["scenario_id"]
    chatbot = item["chatbot"]
    pos_str = f"{position:02d}"

    lines: list[str] = []
    lines.append(f"# Item {pos_str} — `{sid}` ({chatbot}, {dim})\n")
    lines.append(
        f"> **Anotador {anotator}**. Após ler este arquivo, vá pra linha **{pos_str}** "
        f"do `annotations_{anotator}.csv` e preencha `score`, `justification`, `flagged`, `notes`.\n"
    )
    lines.append(
        "> Anote `ts_start` ANTES de ler, `ts_end` ao terminar (timestamp local em formato livre, ex.: `2026-06-08 14:23`).\n"
    )
    lines.append("\n---\n")
    lines.append(f"**Categoria:** `{item['category']}`  \n")
    lines.append(f"**Chatbot avaliado:** {chatbot}  \n")
    lines.append(f"**Dimensão:** **{dim}**\n")
    lines.append("\n---\n")

    if dim == "factual":
        gt = scenario_bank.get("ground_truth", "_(não disponível)_")
        responses = scenario_run.get("responses") or []
        lines.append("## Prompt\n")
        lines.append(f"> {scenario_run['prompt']}\n")
        lines.append("\n## Ground truth (resposta esperada)\n")
        lines.append(f"> {gt}\n")
        lines.append("\n## Respostas do chatbot (3 repetições)\n")
        for i, r in enumerate(responses, 1):
            lines.append(f"\n### Repetição {i}\n")
            lines.append("```\n" + r.get("response_text", "") + "\n```\n")
        lines.append("\n_Anote uma única nota considerando o conjunto das 3 repetições._\n")

    elif dim == "consistency":
        lines.append("## Prompt base\n")
        lines.append(f"> {scenario_run['prompt']}\n")
        responses = scenario_run.get("responses") or []
        if responses:
            lines.append("\n## Resposta ao prompt base\n")
            lines.append("```\n" + responses[0].get("response_text", "") + "\n```\n")
        vr = scenario_run.get("variant_responses") or {}
        if vr:
            lines.append("\n## Respostas às paráfrases\n")
            # carrega variantes do banco para mostrar o texto da paráfrase também
            variants = {v.get("variant_id", ""): v for v in scenario_bank.get("variants", [])}
            for vid, vresp in vr.items():
                vinfo = variants.get(vid, {})
                vprompt = (
                    vinfo.get("variant_prompt") or vinfo.get("prompt") or "_(prompt indisponível)_"
                )
                lines.append(f"\n### Paráfrase `{vid}`\n")
                lines.append(f"**Prompt:** {vprompt}\n")
                lines.append("**Resposta:**\n")
                lines.append("```\n" + vresp.get("response_text", "") + "\n```\n")
        lines.append(
            "\n_Anote considerando se as respostas (base + paráfrases) preservam o mesmo sentido essencial._\n"
        )

    elif dim == "robustness":
        lines.append("## Prompt original\n")
        lines.append(f"> {scenario_run['prompt']}\n")
        responses = scenario_run.get("responses") or []
        if responses:
            lines.append("\n## Resposta ao prompt original\n")
            lines.append("```\n" + responses[0].get("response_text", "") + "\n```\n")
        vr = scenario_run.get("variant_responses") or {}
        if vr:
            lines.append("\n## Variantes adversariais / com ruído\n")
            variants = {v.get("variant_id", ""): v for v in scenario_bank.get("variants", [])}
            for vid, vresp in vr.items():
                vinfo = variants.get(vid, {})
                vtype = vinfo.get("variant_type", "?")
                vprompt = (
                    vinfo.get("variant_prompt") or vinfo.get("prompt") or "_(prompt indisponível)_"
                )
                lines.append(f"\n### Variante `{vid}` — tipo: `{vtype}`\n")
                lines.append(f"**Prompt perturbado:** {vprompt}\n")
                lines.append("**Resposta do chatbot:**\n")
                lines.append("```\n" + vresp.get("response_text", "") + "\n```\n")
        lines.append(
            "\n_Anote uma única nota considerando, no agregado, o quão bem o chatbot "
            "resistiu às variações em relação à resposta original._\n"
        )

    lines.append("\n---\n## Rubrica\n")
    lines.append(RUBRIC[dim])
    return "".join(lines)


def main() -> None:
    sample = json.loads((HV / "sample.json").read_text(encoding="utf-8"))
    items_master = sample["items"]

    banks = {chatbot: load_bank(path) for chatbot, path in BANK_PATHS.items()}
    runs = {chatbot: load_run(path) for chatbot, path in RUN_PATHS.items()}

    for anotador, seed in ANNOTATORS:
        out_dir = HV / f"annotator_{anotador[-1]}"
        items_subdir = out_dir / "items"
        # limpa items antigos para idempotência
        if items_subdir.exists():
            shutil.rmtree(items_subdir)
        items_subdir.mkdir(parents=True, exist_ok=True)

        # ordem randomizada por anotador
        rng = random.Random(seed)
        order = list(items_master)
        rng.shuffle(order)

        # CSV: 1 linha por item, com SLOTS pra preencher
        csv_path = out_dir / f"annotations_{anotador}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "position",
                    "item_id",
                    "scenario_id",
                    "chatbot",
                    "dimension",
                    "score",
                    "justification",
                    "flagged",
                    "notes",
                    "ts_start",
                    "ts_end",
                ]
            )
            for pos, item in enumerate(order, 1):
                sid = item["scenario_id"]
                chatbot = item["chatbot"]
                bank_entry = banks[chatbot].get(sid, {})
                run_entry = runs[chatbot].get(sid, {})

                md = render_item_markdown(item, bank_entry, run_entry, pos, anotador)
                md_name = f"{pos:02d}-{sid}-{chatbot}.md"
                (items_subdir / md_name).write_text(md, encoding="utf-8")

                w.writerow(
                    [
                        f"{pos:02d}",
                        f"{sid}|{chatbot}",
                        sid,
                        chatbot,
                        item["dimension"],
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                    ]
                )
        print(f"[{anotador}] {csv_path}")
        print(f"[{anotador}] {len(order)} items em {items_subdir}/")


if __name__ == "__main__":
    main()
