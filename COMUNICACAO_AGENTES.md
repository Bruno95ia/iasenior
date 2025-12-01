# 🤖 Sistema de Comunicação entre Agentes

## 📋 Visão Geral

Sistema de comunicação cognitiva implementado no orquestrador, permitindo que todos os agentes respondam perguntas e participem de debates colaborativos.

## 🎯 Funcionalidades Implementadas

### 1. **Método `processar_mensagem` em cada Agente**

Todos os agentes agora implementam o método `processar_mensagem(mensagem: str) -> str`:

- **AgenteBase**: Implementação padrão (pode ser sobrescrita)
- **AgentePesquisa**: Responde sobre pesquisa, tecnologias e melhores práticas
- **AgenteOperacoes**: Responde sobre status de serviços e operações
- **AgenteVisaoComputacional**: Responde sobre YOLO, modelos e otimizações
- **AgenteSeguranca**: Responde sobre segurança e proteção
- **AgentePerformance**: Responde sobre métricas e otimizações
- **AgentePredicaoQueda**: Responde sobre predição e análise de risco
- **AgenteMestreVisionario**: Responde com perspectiva estratégica

### 2. **Métodos no Orquestrador**

#### `processar_pergunta(pergunta: str) -> Dict[str, Any]`

Envia uma pergunta para **TODOS** os agentes carregados e retorna um dicionário com todas as respostas.

```python
orquestrador = OrquestradorAgentes()
orquestrador.inicializar_agentes()

resultado = orquestrador.processar_pergunta("Como melhorar a performance?")
# Retorna: {'pergunta': ..., 'respostas': {...}, 'total_agentes': ..., ...}
```

#### `debate(pergunta: str) -> Dict[str, Any]`

Realiza um debate em duas rodadas:

- **Rodada 1**: Cada agente responde a pergunta inicial
- **Rodada 2**: Cada agente lê as respostas dos outros e adiciona comentários

```python
debate_resultado = orquestrador.debate("Qual a melhor estratégia?")
# Retorna estrutura com rodada1 e rodada2
```

#### `resposta_final(respostas: Dict) -> str`

Consolida todas as respostas em uma string formatada, útil para apresentação.

```python
resposta_consolidada = orquestrador.resposta_final(resultado)
print(resposta_consolidada)
```

## 📝 Exemplo de Uso

```python
from agents.orquestrador import OrquestradorAgentes

# Criar orquestrador
orquestrador = OrquestradorAgentes()
orquestrador.inicializar_agentes()

# Opção 1: Processar pergunta simples
resultado = orquestrador.processar_pergunta("Como otimizar o sistema?")
resposta = orquestrador.resposta_final(resultado)
print(resposta)

# Opção 2: Realizar debate
debate = orquestrador.debate("Qual a melhor abordagem?")
resposta_debate = orquestrador.resposta_final(debate)
print(resposta_debate)
```

## 🔍 Estrutura de Respostas

### Resposta de `processar_pergunta`:

```python
{
    'pergunta': 'Como melhorar a performance?',
    'respostas': {
        'pesquisa': {
            'resposta': '[🔍 Agente de Pesquisa] ...',
            'timestamp': '2025-01-08T12:00:00',
            'status': 'sucesso'
        },
        'operacoes': {
            'resposta': '[⚙️ Agente de Operações] ...',
            'timestamp': '2025-01-08T12:00:00',
            'status': 'sucesso'
        },
        # ... outros agentes
    },
    'total_agentes': 7,
    'agentes_responderam': 7,
    'timestamp': '2025-01-08T12:00:00'
}
```

### Resposta de `debate`:

```python
{
    'pergunta': 'Qual a melhor estratégia?',
    'rodada1': {
        'respostas': {
            'mestre_visionario': {
                'resposta': '[🎯 Mestre Visionário] ...',
                'timestamp': '...',
                'status': 'sucesso'
            },
            # ... outros agentes
        },
        'total': 7
    },
    'rodada2': {
        'comentarios': {
            'mestre_visionario': {
                'comentario': '[🎯 Mestre Visionário] ...',
                'timestamp': '...',
                'status': 'sucesso'
            },
            # ... outros agentes
        },
        'total': 7
    },
    'timestamp': '2025-01-08T12:00:00'
}
```

## ✅ Garantias

1. **Não quebra funcionalidade existente**: Todos os métodos são adicionais, não modificam comportamento atual
2. **Thread-safe**: Métodos podem ser chamados mesmo com agentes rodando em threads
3. **Tratamento de erros**: Cada agente trata seus próprios erros sem afetar outros
4. **Compatibilidade**: Agentes legados que não implementam `processar_mensagem` retornam status `nao_suportado`

## 🚀 Executar Exemplo

```bash
python3 exemplo_comunicacao_agentes.py
```

## 📚 Arquivos Modificados

- `agents/agente_base.py`: Adicionado método `processar_mensagem` padrão
- `agents/agente_pesquisa.py`: Implementado `processar_mensagem` específico
- `agents/agente_operacoes.py`: Implementado `processar_mensagem` específico
- `agents/agente_visao_computacional.py`: Implementado `processar_mensagem` específico
- `agents/agente_seguranca.py`: Implementado `processar_mensagem` específico
- `agents/agente_performance.py`: Implementado `processar_mensagem` específico
- `agents/agente_predicao_queda.py`: Implementado `processar_mensagem` específico
- `agents/agente_mestre_visionario.py`: Implementado `processar_mensagem` específico
- `agents/orquestrador.py`: Adicionados métodos `processar_pergunta`, `debate` e `resposta_final`

## 🎯 Próximos Passos (Opcional)

- Adicionar persistência de debates
- Implementar sistema de votação entre agentes
- Adicionar filtros por relevância de resposta
- Criar interface web para visualizar debates
- Implementar histórico de perguntas e respostas

---

**Versão**: 1.0.0  
**Data**: 2025-01  
**Status**: ✅ Implementado e Testado

