# MCP Listener Plugin

Plugin listener per Model Context Protocol. Riceve messaggi e comandi da client MCP e triggera workflow automaticamente per integrazione con sistemi AI e modelli linguistici.

## Caratteristiche

- ✅ Supporto Model Context Protocol
- ✅ Comunicazione bidirezionale con AI models
- ✅ Gestione contesto conversazionale
- ✅ Autenticazione token-based
- ✅ Routing messaggi intelligente
- ✅ Integration con LLM providers

## Configurazione

### Parametri Obbligatori

- `endpoint`: Endpoint MCP su cui ascoltare

### Parametri Opzionali

- `auth_token`: Token di autenticazione per connessioni MCP

## Variabili Iniettate

- `mcp_message`: Messaggio ricevuto via MCP
- `mcp_client_id`: ID del client che ha inviato il messaggio
- `mcp_command`: Comando MCP ricevuto
- `mcp_context`: Contesto del messaggio MCP

## Esempio di Utilizzo

```yaml
listener:
  type: mcp
  endpoint: /mcp/assistant
  auth_token: "{MCP_AUTH_TOKEN}"

states:
  - name: process_ai_request
    type: llm-agent
    model: gpt-4
    prompt: "Process this MCP request: $mcp_message"
    context: "$mcp_context"
```

## Integrazione con AI Models

### OpenAI GPT Integration
```yaml
listener:
  type: mcp
  endpoint: /mcp/openai
  
states:
  - name: openai_completion
    type: openai-completion
    model: gpt-4
    messages:
      - role: system
        content: "You are an AI assistant integrated via MCP"
      - role: user  
        content: "$mcp_message"
```

### Anthropic Claude Integration
```yaml
listener:
  type: mcp
  endpoint: /mcp/claude
  
states:
  - name: claude_completion
    type: anthropic-completion
    model: claude-3-sonnet
    prompt: "Handle this MCP request: $mcp_message"
```

### Local LLM Integration
```yaml
listener:
  type: mcp
  endpoint: /mcp/ollama
  
states:
  - name: local_llm
    type: ollama-completion
    model: llama2
    prompt: "Process: $mcp_message"
```

## Casi d'Uso

### AI Assistant Workflow
```yaml
listener:
  type: mcp
  endpoint: /mcp/assistant
  
states:
  - name: understand_intent
    type: llm-agent
    model: gpt-4
    prompt: "Analyze intent: $mcp_message"
    
  - name: execute_action
    type: switch
    variable: intent
    cases:
      query: { type: search, query: "$mcp_message" }
      command: { type: shell, command: "$extracted_command" }
      creative: { type: generate, prompt: "$mcp_message" }
```

### Code Analysis Tool
```yaml
listener:
  type: mcp
  endpoint: /mcp/code-review
  
states:
  - name: analyze_code
    type: llm-agent
    model: gpt-4
    prompt: "Review this code: $mcp_message"
    
  - name: provide_feedback
    type: mcp-response
    message: "$analysis_result"
```

### Document Processing
```yaml
listener:
  type: mcp
  endpoint: /mcp/documents
  
states:
  - name: extract_text
    type: document-parser
    input: "$mcp_message"
    
  - name: summarize
    type: llm-agent
    model: gpt-4
    prompt: "Summarize: $extracted_text"
```

## MCP Commands

### Standard Commands
- `chat`: Conversazione con AI
- `complete`: Completamento testo
- `analyze`: Analisi contenuto
- `generate`: Generazione contenuto
- `translate`: Traduzione testo

### Custom Commands
```yaml
states:
  - name: handle_custom_command
    type: switch
    variable: mcp_command
    cases:
      custom_analyze: { type: custom-analysis }
      custom_format: { type: custom-formatting }
      custom_validate: { type: custom-validation }
```

## Context Management

### Conversational Context
```yaml
states:
  - name: maintain_context
    type: context-manager
    conversation_id: "$mcp_client_id"
    context: "$mcp_context"
    
  - name: respond_with_context
    type: llm-agent
    model: gpt-4
    context_aware: true
```

### Session Management
```yaml
states:
  - name: session_handler
    type: session-manager
    session_id: "$mcp_client_id"
    ttl: 3600  # 1 hour
```

## Security

- **Usa token autenticazione** per accesso sicuro
- **Valida input** da client MCP
- **Limita rate** per prevenire abuse
- **Monitora utilizzo** modelli AI
- **Implementa timeout** per richieste lunghe

## Performance

- **Cache risposte** frequenti
- **Usa modelli appropriati** per complessità
- **Implementa queuing** per carichi elevati
- **Monitora latenza** end-to-end