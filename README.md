<div align="center">

<img src="assets/banner.svg" alt="NovaCare AI Agent — Prompt Engineering & Guardrail Architecture" width="100%" />

<br /><br />

![Prompt Engineering](https://img.shields.io/badge/Prompt_Engineering-Production_Grade-00D4FF?style=for-the-badge&logo=openai&logoColor=white)
![AI Agent Architecture](https://img.shields.io/badge/AI_Agent_Architecture-Clara_WhatsApp-6366F1?style=for-the-badge&logo=whatsapp&logoColor=white)
![Anti-Hallucination Guardrails](https://img.shields.io/badge/Anti--Hallucination-Guardrails_Verified-10B981?style=for-the-badge&logo=shield&logoColor=white)
![LGPD Safe](https://img.shields.io/badge/LGPD-Zero_Data_Leak-059669?style=for-the-badge&logo=letsencrypt&logoColor=white)
![Python Tested](https://img.shields.io/badge/Python_3.12-15%2F15_Tests_Passing-3776AB?style=for-the-badge&logo=python&logoColor=white)
![DIO Bradesco IA](https://img.shields.io/badge/DIO_Bradesco_IA-Desafio_Criativo-CC092F?style=for-the-badge&logo=bookstack&logoColor=white)

<br />

### Entrega Oficial do Desafio DIO (Bootcamp Bradesco — Agentes de IA do Zero à Prática)

[![Acessar Entrega Oficial](https://img.shields.io/badge/ACESSAR_DOCUMENTO_OFICIAL-PROMPT__AGENTE__ATENDIMENTO.md-0EA5E9?style=for-the-badge&logo=markdown&logoColor=white)](PROMPT_AGENTE_ATENDIMENTO.md)

</div>

---

## Visão Executiva

Este repositório evolui o **Desafio Criativo: Projetando o Prompt de um Agente de Atendimento ao Cliente** (DIO & Bradesco) muito além de um prompt estático: entrega uma **arquitetura completa, testável e auditável em produção** para a agente **Clara**, da **NovaCare Clínica (Especialidades Médicas e Odontológicas)** no **WhatsApp oficial**.

O projeto combina:
1. **Especificação Oficial nos 3 Passos da DIO** ([`PROMPT_AGENTE_ATENDIMENTO.md`](PROMPT_AGENTE_ATENDIMENTO.md)) — Identidade/Escopo, Regras/Guardrails/Handoff e Prompt Final Unificado com **6 Testes de Estresse & Refinamento**.
2. **Motor Determinístico de Guardrails + Modo LLM Opcional** ([`src/agent_engine.py`](src/agent_engine.py)) — Defesa em profundidade offline em Python puro (zero dependências obrigatórias), com máquina de estados, memória de slots, filtro LGPD, proteção contra Prompt Injection e validador rígido de ≤ 5 linhas.
3. **Simulador Interativo & Modo Auditoria CLI** ([`simulador_agente.py`](simulador_agente.py)) — Conversa ao vivo como paciente no WhatsApp e auditoria automatizada (`--audit`) dos 6 cenários críticos da DIO.
4. **Suíte Automatizada de Testes Unitários** ([`tests/test_agent_guardrails.py`](tests/test_agent_guardrails.py)) — 15 testes em `unittest` validando 100% dos contratos de segurança, privacidade e anti-alucinação.

---

## Arquitetura Cognitiva & Fluxo de Decisão da Agente Clara

```mermaid
flowchart TD
    A["Input WhatsApp (Paciente / Responsável)"] --> B["Camada 1: Filtro LGPD & Sanitização"]
    B -->|"Mascara CPF, Cartão, Senha e Fotos de Exames"| C["Camada 2: Memória de Slots & Classificador de Escopo"]
    C --> D{"Camada 3: Checagem de Risco Clínico / Financeiro"}

    D -->|"Dor Aguda / Sangramento / Trauma / Emergência"| H1["Handoff Imediato: Triagem Clínica"]
    D -->|"Diagnóstico / Prescrição de Medicamento"| H2["Bloqueio Ético + Handoff: Triagem e Recepção"]
    D -->|"Reembolso / Contestação de Cobrança / Glosa"| H3["Handoff Imediato: Recepção Financeira"]

    H1 --> R_H["Transferência Humana com Motivo em 1 Frase + Resumo do Contexto (≤ 5 Linhas)"]
    H2 --> R_H
    H3 --> R_H

    D -->|"Sem Gatilho Crítico"| E{"Camada 4: Defesa Prompt Injection & Lacuna de Dados"}
    E -->|"Tentativa de Injeção / Extração de Prompt"| R_SEC["Bloqueio de Segurança + Redirecionamento ao Escopo (≤ 5 Linhas)"]
    E -->|"Preço Não Tabelado / Agenda em Tempo Real / Subplano"| R_GAP["Admissão Explícita de Lacuna + Oferta de Recepção (≤ 5 Linhas)"]

    E -->|"Dentro das 4 Frentes Autorizadas"| F["Camada 5: Geração Orientada a Slots (Sem Repetir Perguntas)"]
    F --> G["Camada 6: ResponseValidator (≤ 5 Linhas, Zero Alucinação, 1 Pergunta Final)"]
    G --> OUT["Resposta Final Segura no WhatsApp"]
```

---

## Matriz de Guardrails de Produção

| Guardrail | Comportamento Garantido | Validação Automatizada |
| :--- | :--- | :--- |
| **Memória de Slots** | Nunca pergunta novamente especialidade, unidade ou convênio já informados pelo paciente | `test_multiturn_scheduling_does_not_reask_known_slots` |
| **Zero Alucinação** | Nunca inventa horários livres em tempo real, valores fechados (`R$`), cobertura de subplano ou protocolos (`#NC-...`) | `test_admits_no_access_to_implant_price_and_realtime_slot` |
| **LGPD Zero-Leak** | Mascara CPF, cartão, senha e fotos de exames na entrada; nunca solicita nem ecoa dados sensíveis | `test_lgpd_masks_cpf_and_credit_card_and_never_echoes` |
| **Anti-Prompt Injection** | Rejeita tentativas de ignorar regras, mudar de persona ou vazar o system prompt | `test_prompt_injection_with_sensitive_data_is_blocked` |
| **Handoff Humano Obrigatório** | Transfere imediatamente em urgência clínica, pedido de diagnóstico/receita ou contestação financeira com motivo em 1 frase + resumo | `TestMandatoryHumanHandoff` (3 testes) |
| **Mobile-First (≤ 5 Linhas)** | Limite rigoroso de até 5 linhas por resposta, sem gírias, com listas numeradas e 1 única pergunta objetiva | `ResponseValidator.validate()` |

---

## Estrutura do Projeto

```text
ai-customer-support-agent-architect/
├── PROMPT_AGENTE_ATENDIMENTO.md   # Entrega oficial DIO (Passos 1, 2, 3 + 6 Testes de Estresse)
├── README.md                      # Documentação executiva e diagrama de arquitetura cognitiva
├── simulador_agente.py            # CLI interativa WhatsApp + Modo Auditoria (--audit)
├── assets/
│   └── banner.svg                 # Hero banner vetorial 3D isométrico cyber-dark
├── src/
│   ├── __init__.py
│   └── agent_engine.py            # Motor da Agente Clara, Guardrails LGPD, Handoff e Validador
└── tests/
    ├── __init__.py
    └── test_agent_guardrails.py   # Suíte unittest (15 testes de estresse e conformidade)
```

---

## Guia Rápido de Execução & Auditoria

> **Requisitos:** Python 3.10+ (zero dependências externas obrigatórias — 100% biblioteca padrão).

### 1. Clonar o repositório
```bash
git clone https://github.com/lcszero44-cell/ai-customer-support-agent-architect.git
cd ai-customer-support-agent-architect
```

### 2. Executar o Simulador Interativo (Chat ao Vivo com a Clara)
```bash
python simulador_agente.py
```
Ou entrar diretamente no chat simulado de WhatsApp:
```bash
python simulador_agente.py --chat
```
Durante a conversa, utilize `/estado` para inspecionar a memória de slots em tempo real, `/reset` para reiniciar a conversa, `/auditoria` para rodar os testes ou `/sair` para encerrar.

### 3. Rodar o Modo Auditoria (6 Cenários do Passo 3 da DIO)
```bash
python simulador_agente.py --audit
```

### 4. Executar a Suíte Completa de Testes Automatizados
```bash
python -W error -m unittest discover -s tests -v
```

### 5. Modo Híbrido Opcional com Ollama / API Compatível com OpenAI
O motor suporta conexão opcional a uma LLM local (ex.: Ollama) mantendo **todos os guardrails determinísticos e fallback seguro** ativos:
```bash
python simulador_agente.py --chat --llm-url http://localhost:11434/v1/chat/completions --model llama3.2
```

---

## Licença & Créditos

Desenvolvido como arquitetura de referência para o **Bootcamp Bradesco — Agentes de IA do Zero à Prática (DIO)**.  
Consulte o artefato principal em [`PROMPT_AGENTE_ATENDIMENTO.md`](PROMPT_AGENTE_ATENDIMENTO.md).
