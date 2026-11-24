#!/usr/bin/env python3
"""Simulador Interativo & Auditor de Guardrails — Agente Clara (NovaCare Clínica).

Uso:
    python simulador_agente.py           # Abre o menu interativo no terminal
    python simulador_agente.py --audit   # Executa a auditoria dos 6 casos da DIO
    python simulador_agente.py --chat    # Inicia direto o chat ao vivo como paciente
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from src.agent_engine import (
    SYSTEM_PROMPT,
    AgentResponse,
    ClaraAgentEngine,
    OptionalLLMConfig,
    run_audit_suite,
)


def _configure_utf8_console() -> None:
    """Garante renderização correta de acentos e símbolos UTF-8 no Windows/PowerShell."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass


class Palette:
    """Estilização ANSI limpa com desativação segura via --no-color."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled and (os.environ.get("NO_COLOR") is None)

    def _wrap(self, code: str, text: str) -> str:
        if not self.enabled:
            return text
        return f"\033[{code}m{text}\033[0m"

    def cyan(self, text: str) -> str:
        return self._wrap("96", text)

    def green(self, text: str) -> str:
        return self._wrap("92", text)

    def yellow(self, text: str) -> str:
        return self._wrap("93", text)

    def red(self, text: str) -> str:
        return self._wrap("91", text)

    def magenta(self, text: str) -> str:
        return self._wrap("95", text)

    def dim(self, text: str) -> str:
        return self._wrap("2", text)

    def bold(self, text: str) -> str:
        return self._wrap("1", text)


def print_header(p: Palette, llm_config: Optional[OptionalLLMConfig]) -> None:
    """Exibe cabeçalho estilizado do simulador."""
    mode = f"Híbrido (LLM: {llm_config.model} + Guardrails)" if llm_config else "Determinístico Offline (Zero Dependências)"
    print(p.cyan("=" * 78))
    print(p.bold(p.cyan("  NOVACARE CLÍNICA // AGENTE CLARA — SIMULADOR WHATSAPP & AUDITOR GUARDRAILS")))
    print(p.dim(f"  Modo de Execução: {mode}"))
    print(p.cyan("=" * 78))


def print_response_telemetry(p: Palette, resp: AgentResponse) -> None:
    """Exibe painel compacto de telemetria dos guardrails após cada turno."""
    status_badge = p.green("GUARDRAILS OK") if resp.all_guardrails_passed else p.red("FALHA GUARDRAIL")
    handoff_text = p.yellow(f"SIM -> {resp.handoff_target}") if resp.handoff_triggered else p.dim("NÃO")
    lgpd_text = p.red(", ".join(resp.lgpd_flags)) if resp.lgpd_flags else p.green("LIMPO")
    inj_text = p.red("BLOQUEADO") if resp.injection_detected else p.green("NÃO")
    print(
        p.dim(
            f"  [Telemetria] Intenção: {resp.intent} | Linhas: {resp.line_count}/5 | "
            f"Handoff: {handoff_text} | LGPD: {lgpd_text} | Injection: {inj_text} | {status_badge}"
        )
    )


def run_audit_cli(p: Palette, llm_config: Optional[OptionalLLMConfig]) -> int:
    """Executa os 6 testes de estresse do Passo 3 da DIO e imprime o relatório."""
    print_header(p, llm_config)
    print(p.bold("\n  MODO AUDITORIA — Bateria de 6 Testes de Estresse (Passo 3 da DIO)\n"))

    results = run_audit_suite(llm_config=llm_config)
    passed_count = sum(1 for r in results if r.passed)

    for res in results:
        sc = res.scenario
        badge = p.green("[APROVADO]") if res.passed else p.red("[REPROVADO]")
        print(f"  {badge} Caso {sc.case_id}: {p.bold(sc.title)} ({p.cyan(sc.category)})")
        print(p.dim(f"    Paciente : {sc.user_input}"))
        if res.response.lgpd_flags:
            print(p.yellow(f"    LGPD Mask: {res.response.sanitized_input}"))
        print(p.magenta("    Clara    :"))
        for line in res.response.text.splitlines():
            print(f"      | {line}")
        print_response_telemetry(p, res.response)

        checks_str = " ".join(
            f"{p.green('OK') if ok else p.red('FAIL')}:{name}"
            for name, ok in res.response.guardrail_checks.items()
        )
        print(p.dim(f"    Checks   : {checks_str}"))
        if res.failure_reasons:
            for reason in res.failure_reasons:
                print(p.red(f"    Motivo   : {reason}"))
        print()

    print(p.cyan("-" * 78))
    summary_color = p.green if passed_count == len(results) else p.red
    print(
        summary_color(
            p.bold(f"  RESULTADO FINAL DA AUDITORIA: {passed_count}/{len(results)} CENÁRIOS APROVADOS (100% COMPLIANCE)"
                   if passed_count == len(results)
                   else f"  RESULTADO FINAL DA AUDITORIA: {passed_count}/{len(results)} CENÁRIOS APROVADOS")
        )
    )
    print(p.cyan("-" * 78))
    return 0 if passed_count == len(results) else 1


def run_interactive_chat(p: Palette, llm_config: Optional[OptionalLLMConfig]) -> None:
    """Executa sessão de chat ao vivo no WhatsApp simulado com a Agente Clara."""
    engine = ClaraAgentEngine(llm_config=llm_config)
    print(p.bold("\n  CHAT AO VIVO — WhatsApp NovaCare Clínica (Agente Clara)"))
    print(p.dim("  Comandos: /estado (ver memória) | /reset (nova conversa) | /auditoria | /sair\n"))
    print(p.magenta("  Clara:") + " Olá! Sou a Clara, da NovaCare Clínica. Como posso ajudar você hoje?\n")

    while True:
        try:
            user_input = input(p.cyan("  Você > ")).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + p.dim("  Encerrando conversa."))
            return

        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in {"/sair", "/exit", "sair"}:
            print(p.dim("  Conversa encerrada. Obrigado por testar a Agente Clara!"))
            return
        if cmd == "/reset":
            engine.reset()
            print(p.yellow("  [Sistema] Memória da conversa reiniciada.\n"))
            continue
        if cmd == "/estado":
            st = engine.state
            print(p.dim("  [Estado Atual da Conversa]"))
            print(p.dim(f"    Turnos        : {st.turn_count}"))
            print(p.dim(f"    Ação          : {st.action or '-'}"))
            print(p.dim(f"    Especialidade : {st.specialty or '-'}"))
            print(p.dim(f"    Unidade       : {st.unit or '-'}"))
            print(p.dim(f"    Modalidade    : {st.coverage_type or '-'}"))
            print(p.dim(f"    Período       : {st.period_preference or '-'}"))
            print(p.dim(f"    Handoff Ativo : {st.handoff_triggered} ({st.handoff_target or '-'})\n"))
            continue
        if cmd == "/auditoria":
            run_audit_cli(p, llm_config)
            continue

        resp = engine.process_message(user_input)
        print()
        print(p.magenta("  Clara:"))
        for line in resp.text.splitlines():
            print(f"    {line}")
        print_response_telemetry(p, resp)
        print()


def run_menu(p: Palette, llm_config: Optional[OptionalLLMConfig]) -> int:
    """Menu interativo principal do simulador."""
    while True:
        print_header(p, llm_config)
        print("\n  Selecione uma opção:")
        print(f"    {p.cyan('[1]')} Conversar ao vivo com a Agente Clara (Simulador WhatsApp)")
        print(f"    {p.cyan('[2]')} Rodar Auditoria dos 6 Testes de Estresse (Passo 3 da DIO)")
        print(f"    {p.cyan('[3]')} Exibir Prompt Final Unificado de Produção")
        print(f"    {p.cyan('[0]')} Sair\n")

        try:
            choice = input(p.cyan("  Opção > ")).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + p.dim("  Até logo!"))
            return 0

        if choice == "1":
            run_interactive_chat(p, llm_config)
        elif choice == "2":
            run_audit_cli(p, llm_config)
        elif choice == "3":
            print("\n" + p.cyan("-" * 78))
            print(SYSTEM_PROMPT)
            print(p.cyan("-" * 78) + "\n")
        elif choice == "0":
            print(p.dim("  Simulador encerrado."))
            return 0
        else:
            print(p.yellow("  Opção inválida. Escolha 1, 2, 3 ou 0.\n"))


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulador Interativo e Motor de Auditoria da Agente Clara (NovaCare Clínica)."
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Executa automaticamente os 6 cenários de teste do Passo 3 da DIO.",
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Inicia diretamente o modo de conversa interativa como paciente.",
    )
    parser.add_argument(
        "--llm-url",
        default="",
        help="URL opcional de endpoint compatível com OpenAI/Ollama (ex: http://localhost:11434/v1/chat/completions).",
    )
    parser.add_argument(
        "--model",
        default="llama3.2",
        help="Nome do modelo a utilizar quando --llm-url for informado.",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("LLM_API_KEY", ""),
        help="Chave de API opcional (ou defina variável de ambiente LLM_API_KEY).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Desativa cores ANSI na saída do terminal.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    _configure_utf8_console()
    args = parse_args(argv)
    palette = Palette(enabled=not args.no_color)

    llm_config: Optional[OptionalLLMConfig] = None
    if args.llm_url:
        llm_config = OptionalLLMConfig(
            endpoint_url=args.llm_url,
            model=args.model,
            api_key=args.api_key,
        )

    if args.audit:
        return run_audit_cli(palette, llm_config)
    if args.chat:
        print_header(palette, llm_config)
        run_interactive_chat(palette, llm_config)
        return 0
    return run_menu(palette, llm_config)


if __name__ == "__main__":
    raise SystemExit(main())
