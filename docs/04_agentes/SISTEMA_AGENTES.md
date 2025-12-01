# 🤖 Sistema de Agentes Inteligentes - IASenior

## 📋 Visão Geral

O IASenior possui um sistema completo de agentes inteligentes especializados que trabalham colaborativamente para analisar, melhorar e operar o sistema. Este documento consolida toda a documentação sobre agentes.

## 🎯 Agentes Disponíveis

### 1. 🔍 Agente de Pesquisa
- **Função**: Pesquisa documentação, tecnologias e melhores práticas
- **Especialidade**: Análise de documentação e estrutura do projeto
- **Sugestões**: Melhorias em documentação e organização

### 2. 👁️ Agente de Visão Computacional
- **Função**: Analisa modelos YOLO e scripts de inferência
- **Especialidade**: Otimizações de modelos e performance de detecção
- **Sugestões**: Melhorias em modelos, cache e métricas

### 3. ⚙️ Agente de Operações
- **Função**: Monitora serviços, logs e scripts de gerenciamento
- **Especialidade**: Operações e infraestrutura
- **Sugestões**: Melhorias em monitoramento e deploy

### 4. 🔒 Agente de Segurança
- **Função**: Analisa vulnerabilidades e práticas de segurança
- **Especialidade**: Segurança e proteção
- **Sugestões**: Melhorias de segurança e boas práticas

### 5. ⚡ Agente de Performance
- **Função**: Coleta métricas e analisa otimizações
- **Especialidade**: Performance e otimização
- **Sugestões**: Otimizações de performance e métricas

### 6. 🧠 Agente de Predição de Quedas
- **Função**: Analisa modelos de ML e datasets
- **Especialidade**: Machine Learning e predição
- **Sugestões**: Melhorias em modelos de ML e datasets

### 7. 🎯 Mestre Visionário (Orquestrador)
- **Função**: Orquestra todos os agentes e fornece perspectiva estratégica
- **Especialidade**: Visão estratégica e coordenação
- **Sugestões**: Melhorias estratégicas e arquiteturais

---

## 💬 Sistema de Comunicação

### Processar Perguntas

Todos os agentes implementam o método `processar_mensagem(mensagem: str)` que permite comunicação direta:

```python
from agents.orquestrador import OrquestradorAgentes

orquestrador = OrquestradorAgentes()
orquestrador.inicializar_agentes()

# Enviar pergunta para todos os agentes
resultado = orquestrador.processar_pergunta("Como melhorar a performance?")
resposta = orquestrador.resposta_final(resultado)
print(resposta)
```

### Debates Colaborativos

Sistema de debate em múltiplas rodadas onde agentes respondem, comentam e refinam:

```python
# Debate em 2 rodadas
debate = orquestrador.debate("Qual a melhor estratégia?")
resposta = orquestrador.resposta_final(debate)
```

**Estrutura do Debate:**
- **Rodada 1**: Cada agente responde à pergunta inicial
- **Rodada 2**: Cada agente lê as respostas dos outros e adiciona comentários
- **Rodada 3** (CLI): Refinamento e síntese final

---

## 🤝 Sessões Colaborativas

### Executar Sessão Colaborativa

```bash
python3 examples/sessao_colaborativa_agentes.py
```

### O que acontece?

1. **FASE 1: Análise Individual**
   - Cada agente analisa o projeto independentemente
   - Agentes examinam suas áreas de expertise

2. **FASE 2: Compartilhamento**
   - Agentes compartilham suas descobertas
   - Cada agente apresenta observações e sugestões

3. **FASE 3: Discussão Colaborativa**
   - Agentes discutem melhorias juntos
   - Categorização de melhorias por área
   - Identificação de consensos

4. **FASE 4: Priorização**
   - Melhorias são priorizadas por importância
   - Ranking das top 10 melhorias

### Resultados

Os resultados são salvos em:
- `agents_data/sessao_colaborativa/sessao_YYYYMMDD_HHMMSS.json` - Dados completos
- `agents_data/sessao_colaborativa/relatorio_YYYYMMDD_HHMMSS.md` - Relatório em Markdown

---

## 🖥️ CLI de Debate

### Instalação

```bash
pip install colorama
```

### Uso

```bash
python3 examples/cli_debate_3rodadas.py
```

### Funcionalidades

- **3 Rodadas de Debate**: Respostas iniciais, comentários e refinamento
- **Interface Colorida**: Cores diferentes para cada rodada
- **Animação de Digitação**: Efeito visual de typing
- **Comandos**: Digite sua pergunta ou `sair` para encerrar

### Exemplo

```
❓ Sua Pergunta: Como melhorar a performance do sistema?

📊 RODADA 1: Respostas Iniciais
[Agentes respondem...]

💬 RODADA 2: Comentários e Perspectivas
[Agentes comentam...]

🎯 RODADA 3: Refinamento e Síntese
[Agentes refinam...]

📋 CONSOLIDAÇÃO FINAL
[Resposta consolidada...]
```

---

## 📚 Arquivos Relacionados

### Código
- `agents/agente_base.py` - Classe base para todos os agentes
- `agents/orquestrador.py` - Orquestrador de agentes
- `agents/agente_*.py` - Implementações específicas de cada agente

### Exemplos
- `examples/exemplo_comunicacao_agentes.py` - Exemplo de comunicação
- `examples/sessao_colaborativa_agentes.py` - Sessão colaborativa
- `examples/cli_debate_3rodadas.py` - CLI de debate

### Documentação Antiga (Consolidada)
- ~~`COLABORACAO_AGENTES.md`~~ → Consolidado neste documento
- ~~`COMUNICACAO_AGENTES.md`~~ → Consolidado neste documento
- ~~`COMO_USAR_CLI.md`~~ → Consolidado neste documento
- ~~`README_CLI_DEBATE.md`~~ → Consolidado neste documento

---

## 🎯 Próximos Passos

1. Execute uma sessão colaborativa para analisar o projeto
2. Use o CLI de debate para fazer perguntas aos agentes
3. Revise os relatórios gerados em `agents_data/sessao_colaborativa/`
4. Implemente as melhorias sugeridas pelos agentes

---

**Versão**: 2.0  
**Data**: Janeiro 2025  
**Status**: ✅ Consolidado e Organizado


