# 🔊 Text-to-Speech Plugin v1.0.0

Plugin avanzato per convertire testo in audio utilizzando l'API di ElevenLabs. Genera file MP3 di alta qualità nella cartella workspace con supporto per diverse voci e lingue.

## ✨ Caratteristiche

- ✅ **Integrazione ElevenLabs API** - Utilizza l'API di ElevenLabs per TTS di alta qualità
- ✅ **Supporto Multi-Voce** - Selezione tra diverse voci disponibili
- ✅ **Supporto Multi-Lingua** - Supporta diverse lingue tramite modelli ElevenLabs
- ✅ **Gestione File Automatica** - Creazione automatica della cartella workspace
- ✅ **Naming Flessibile** - Timestamp automatico + prefisso opzionale
- ✅ **Configurazione Avanzata** - Impostazioni personalizzabili per la voce
- ✅ **Gestione Errori Robusta** - Logging dettagliato e gestione errori completa
- ✅ **Output Strutturato** - Risultati dettagliati salvati nelle variabili

## 📋 Requisiti

- **Python 3.8+**
- **Account ElevenLabs** con API key attiva
- **Librerie**: `requests>=2.25.0`

## 🚀 Installazione

### Metodo 1: Package Manager (Raccomandato)

```yaml
# plugins.yaml
dependencies:
  - text-to-speech>=1.0.0
```

```bash

```

### Metodo 2: Installazione Manuale

1. Copia la cartella `text-to-speech/` in `custom_states/`
2. Riavvia l'applicazione

## ⚙️ Configurazione

### Variabili d'Ambiente

Aggiungi la tua API key di ElevenLabs al file `.env`:

```env
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

### Ottenere l'API Key

1. Registrati su [ElevenLabs](https://elevenlabs.io/)
2. Vai su **Profile Settings** → **API Keys**
3. Crea una nuova API key
4. Copia la key nel file `.env`

## 📖 Utilizzo

### Esempio Base

```yaml
states:
  generate_audio:
    state_type: "text_to_speech"
    api_key: "{ELEVENLABS_API_KEY}"
    text: "Ciao, questo è un test di text-to-speech!"
    transition: "next_step"
```

### Esempio con Voce Personalizzata

```yaml
states:
  custom_voice_audio:
    state_type: "text_to_speech"
    api_key: "{ELEVENLABS_API_KEY}"
    text: "Hello, this is a custom voice test!"
    voice_id: "EXAVITQu4vr4xnSDxMaL"  # Sarah
    filename_prefix: "custom_voice"
    output: "tts_result"
    success_transition: "success"
    error_transition: "error"
```

### Esempio Avanzato

```yaml
states:
  advanced_tts:
    state_type: "text_to_speech"
    api_key: "{ELEVENLABS_API_KEY}"
    text: "Questo è un esempio con impostazioni avanzate della voce."
    voice_id: "21m00Tcm4TlvDq8ikWAM"  # Rachel
    model_id: "eleven_multilingual_v2"
    voice_settings:
      stability: 0.5
      similarity_boost: 0.75
      style: 0.0
      use_speaker_boost: true
    filename_prefix: "advanced_tts"
    workspace_path: "audio_output"
    output: "advanced_result"
    transition: "next_step"
```

## 🎯 Parametri

### Obbligatori

| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `api_key` | string | API key di ElevenLabs. Usa `{ELEVENLABS_API_KEY}` |
| `text` | string | Testo da convertire in audio |

### Opzionali

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `voice_id` | string | `21m00Tcm4TlvDq8ikWAM` | ID della voce ElevenLabs |
| `model_id` | string | `eleven_monolingual_v1` | Modello ElevenLabs da utilizzare |
| `voice_settings` | object | `{"stability": 0.5, "similarity_boost": 0.75}` | Impostazioni della voce |
| `filename_prefix` | string | - | Prefisso per il nome del file |
| `workspace_path` | string | `workspace` | Cartella dove salvare i file |
| `output` | string | - | Variabile per salvare il risultato |
| `success_transition` | string | - | Stato successivo in caso di successo |
| `error_transition` | string | - | Stato successivo in caso di errore |

### Voice Settings

```yaml
voice_settings:
  stability: 0.5          # 0.0-1.0, stabilità della voce
  similarity_boost: 0.75  # 0.0-1.0, somiglianza alla voce originale
  style: 0.0             # 0.0-1.0, stile della voce (solo alcuni modelli)
  use_speaker_boost: true # Migliora la chiarezza della voce
```

## 🎤 Voci Disponibili

### Voci Popolari

| Nome | Voice ID | Lingua | Descrizione |
|------|----------|--------|-------------|
| Rachel | `21m00Tcm4TlvDq8ikWAM` | EN | Voce femminile americana |
| Drew | `29vD33N1CtxCmqQRPOHJ` | EN | Voce maschile americana |
| Clyde | `2EiwWnXFnvU5JabPnv8n` | EN | Voce maschile americana |
| Paul | `5Q0t7uMcjvnagumLfvZi` | EN | Voce maschile americana |
| Domi | `AZnzlk1XvdvUeBnXmlld` | EN | Voce femminile americana |
| Dave | `CYw3kZ02Hs0563khs1Fj` | EN | Voce maschile britannica |
| Fin | `D38z5RcWu1voky8WS1ja` | EN | Voce maschile irlandese |
| Sarah | `EXAVITQu4vr4xnSDxMaL` | EN | Voce femminile americana |
| Antoni | `ErXwobaYiN019PkySvjV` | EN | Voce maschile americana |
| Thomas | `GBv7mTt0atIp3Br8iCZE` | EN | Voce maschile americana |

> **Nota**: Per ottenere la lista completa delle voci disponibili, usa l'API ElevenLabs `/voices`

## 🔧 Modelli Disponibili

| Modello | Descrizione | Lingue |
|---------|-------------|--------|
| `eleven_monolingual_v1` | Modello monolingua inglese (veloce) | EN |
| `eleven_multilingual_v1` | Modello multilingua (qualità standard) | Multi |
| `eleven_multilingual_v2` | Modello multilingua avanzato (alta qualità) | Multi |
| `eleven_turbo_v2` | Modello veloce multilingua | Multi |

## 📁 Struttura File Output

```
workspace/
├── 20240115_143022.mp3                    # Solo timestamp
├── custom_voice_20240115_143045.mp3       # Con prefisso
└── advanced_tts_20240115_143102.mp3       # Con prefisso personalizzato
```

## 📊 Output del Plugin

Quando specifichi il parametro `output`, il plugin salva i seguenti dati:

### Successo

```json
{
  "success": true,
  "filepath": "workspace/custom_voice_20240115_143045.mp3",
  "filename": "custom_voice_20240115_143045.mp3",
  "workspace_path": "workspace",
  "file_size": 245760,
  "voice_id": "EXAVITQu4vr4xnSDxMaL",
  "model_id": "eleven_monolingual_v1",
  "text_length": 35,
  "message": "Audio generato con successo"
}
```

### Errore

```json
{
  "success": false,
  "error": "Errore HTTP durante la chiamata a ElevenLabs: 401 Client Error",
  "status_code": 401,
  "voice_id": "EXAVITQu4vr4xnSDxMaL",
  "text_length": 35
}
```

## 🔄 Workflow Completo

```yaml
# workflow_tts.yaml
listener:
  type: "webhook"
  port: 8080

variables:
  elevenlabs_key: "{ELEVENLABS_API_KEY}"
  input_text: "Benvenuto nel sistema di automazione IntellyHub!"

states:
  start:
    state_type: "text_to_speech"
    api_key: "{elevenlabs_key}"
    text: "{input_text}"
    voice_id: "21m00Tcm4TlvDq8ikWAM"
    filename_prefix: "welcome"
    output: "tts_result"
    success_transition: "success"
    error_transition: "error"

  success:
    state_type: "command"
    action:
      eval: "print(f'✅ Audio generato: {tts_result[\"filepath\"]} ({tts_result[\"file_size\"]} bytes)')"
    transition: "end"

  error:
    state_type: "command"
    action:
      eval: "print(f'❌ Errore TTS: {tts_result[\"error\"]}')"
    transition: "end"

  end:
    state_type: "end"
```

## 🚨 Gestione Errori

Il plugin gestisce diversi tipi di errori:

### Errori di Autenticazione (401)
- API key non valida o scaduta
- Quota API esaurita

### Errori di Validazione (400)
- Testo troppo lungo
- Voice ID non valido
- Parametri malformati

### Errori di Connessione
- Problemi di rete
- Timeout API

### Errori di Sistema
- Problemi di scrittura file
- Cartella workspace non accessibile

## 💡 Best Practices

### 1. Gestione API Key
```yaml
# ✅ Corretto - usa variabili d'ambiente
api_key: "{ELEVENLABS_API_KEY}"

# ❌ Evita - non hardcodare la key
api_key: "sk-1234567890abcdef"
```

### 2. Gestione Errori
```yaml
states:
  tts_step:
    state_type: "text_to_speech"
    # ... parametri ...
    success_transition: "process_audio"
    error_transition: "handle_error"
```

### 3. Ottimizzazione Costi
```yaml
# Usa modelli più veloci per testi semplici
model_id: "eleven_turbo_v2"

# Usa modelli avanzati solo quando necessario
model_id: "eleven_multilingual_v2"
```

### 4. Organizzazione File
```yaml
# Usa prefissi descrittivi
filename_prefix: "notification"
workspace_path: "audio/notifications"
```

## 🔍 Troubleshooting

### Problema: "API key non valida"
**Soluzione**: Verifica che l'API key sia corretta e attiva nel tuo account ElevenLabs.

### Problema: "Voice ID non trovato"
**Soluzione**: Controlla che il voice_id sia corretto. Usa l'API `/voices` per ottenere la lista.

### Problema: "Quota API esaurita"
**Soluzione**: Controlla il tuo piano ElevenLabs e i limiti di utilizzo.

### Problema: "File non creato"
**Soluzione**: Verifica i permessi della cartella workspace e lo spazio disco disponibile.

## 📚 Risorse Utili

- [ElevenLabs API Documentation](https://elevenlabs.io/docs)
- [ElevenLabs Voice Library](https://elevenlabs.io/voice-library)
- [ElevenLabs Pricing](https://elevenlabs.io/pricing)

## 🤝 Contributi

Per contribuire al plugin:

1. Fork del repository
2. Crea un branch per la tua feature
3. Implementa le modifiche
4. Aggiungi test se necessario
5. Crea una Pull Request

## 📄 Licenza

Questo plugin è distribuito sotto licenza MIT.

---

**Sviluppato con ❤️ per la community IntellyHub**
