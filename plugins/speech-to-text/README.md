# 🎤 Speech-to-Text Plugin per IntellyHub

Plugin per convertire audio in testo utilizzando OpenAI Whisper API. Supporta diversi formati audio, lingue multiple e rilevamento automatico della lingua.

## 🚀 Caratteristiche

- **Supporto multi-formato**: MP3, WAV, M4A, FLAC, OGG, WebM e altri
- **Rilevamento automatico lingua**: Supporta 99+ lingue
- **File locali e remoti**: Trascrizione da file locali o URL
- **Formati output multipli**: JSON, testo, SRT, VTT per sottotitoli
- **Gestione errori robusta**: Validazione file e gestione eccezioni
- **Performance ottimizzate**: Gestione file fino a 25MB

## 📋 Requisiti

- **API Key OpenAI**: Necessaria per accedere a Whisper API
- **Python**: >= 3.7
- **Dipendenze**: `requests>=2.25.0`, `openai>=1.0.0`

## 🛠️ Installazione

### Installazione Automatica
```bash
# Aggiungi al file plugins.yaml
echo "dependencies:
  - speech-to-text>=1.0.0" >> plugins.yaml

# Installa il plugin
python main.py plugins install
```

### Configurazione
```bash
# Imposta la variabile d'ambiente per l'API key
export OPENAI_API_KEY="your-openai-api-key-here"
```

## 📖 Utilizzo

### Esempio Base
```yaml
variables:
  audio_file: "workspace/recording.mp3"

states:
  transcribe_audio:
    state_type: "speech_to_text"
    api_key: "{OPENAI_API_KEY}"
    audio_file: "{audio_file}"
    output: "transcription"
    transition: "process_text"
  
  process_text:
    state_type: "command"
    action:
      eval: "print(f'Testo trascritto: {transcription[text]}')"
    transition: "end"
  
  end:
    state_type: "end"
```

### Esempio con Lingua Specifica
```yaml
states:
  transcribe_italian:
    state_type: "speech_to_text"
    api_key: "{OPENAI_API_KEY}"
    audio_file: "workspace/italian_audio.wav"
    language: "it"
    response_format: "verbose_json"
    output: "detailed_transcription"
    success_transition: "analyze_text"
    error_transition: "handle_error"
```

### Esempio da URL Remoto
```yaml
states:
  transcribe_remote:
    state_type: "speech_to_text"
    api_key: "{OPENAI_API_KEY}"
    audio_file: "https://example.com/podcast.mp3"
    language: "en"
    prompt: "This is a technical podcast about AI and machine learning."
    temperature: 0.1
    response_format: "srt"
    output: "subtitle_transcription"
    transition: "save_subtitles"
```

### Esempio Avanzato con Gestione Errori
```yaml
variables:
  audio_files:
    - "workspace/audio1.mp3"
    - "workspace/audio2.wav"
    - "https://example.com/remote_audio.ogg"

states:
  process_audio_batch:
    state_type: "loop"
    loop_type: "for"
    items: "{audio_files}"
    item_var: "current_audio"
    body_state: "transcribe_single"
    transition: "batch_complete"
  
  transcribe_single:
    state_type: "speech_to_text"
    api_key: "{OPENAI_API_KEY}"
    audio_file: "{current_audio}"
    language: "auto"
    response_format: "verbose_json"
    workspace_path: "transcription_workspace"
    output: "current_transcription"
    success_transition: "save_result"
    error_transition: "log_error"
  
  save_result:
    state_type: "command"
    action:
      eval: |
        results = variables.get('batch_results', [])
        results.append({
          'file': current_audio,
          'transcription': current_transcription,
          'status': 'success'
        })
        variables['batch_results'] = results
    transition: "continue_loop"
  
  log_error:
    state_type: "command"
    action:
      eval: |
        errors = variables.get('batch_errors', [])
        errors.append({
          'file': current_audio,
          'error': current_transcription.get('error', 'Unknown error'),
          'status': 'failed'
        })
        variables['batch_errors'] = errors
    transition: "continue_loop"
```

## 🎛️ Parametri

### Obbligatori
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `api_key` | string | API key OpenAI per Whisper |
| `audio_file` | string | Percorso file audio o URL |

### Opzionali
| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `language` | string | "auto" | Codice lingua ISO 639-1 |
| `model` | string | "whisper-1" | Modello Whisper da usare |
| `response_format` | string | "json" | Formato output (json, text, srt, vtt, verbose_json) |
| `temperature` | float | 0.0 | Creatività trascrizione (0.0-1.0) |
| `workspace_path` | string | "workspace" | Cartella per file temporanei |
| `prompt` | string | - | Prompt per guidare la trascrizione |
| `output` | string | - | Nome variabile per risultato |
| `success_transition` | string | - | Stato successivo se successo |
| `error_transition` | string | - | Stato successivo se errore |

## 📊 Formato Output

### Formato JSON (default)
```json
{
  "success": true,
  "text": "Testo trascritto completo",
  "word_count": 42,
  "processing_time": 3.2,
  "model_used": "whisper-1",
  "file_info": {
    "filename": "audio.mp3",
    "file_size": 1024000,
    "format": "mp3",
    "size_mb": 1.02
  },
  "parameters": {
    "language": "auto-detect",
    "response_format": "json",
    "temperature": 0.0
  }
}
```

### Formato Verbose JSON
```json
{
  "success": true,
  "text": "Testo completo trascritto",
  "language": "it",
  "duration": 45.2,
  "word_count": 42,
  "segments": [
    {
      "id": 0,
      "seek": 0,
      "start": 0.0,
      "end": 3.5,
      "text": "Primo segmento di testo",
      "tokens": [50364, 50365, ...],
      "temperature": 0.0,
      "avg_logprob": -0.3,
      "compression_ratio": 1.2,
      "no_speech_prob": 0.01
    }
  ],
  "processing_time": 4.1,
  "model_used": "whisper-1",
  "file_info": {...}
}
```

### Formato SRT (Sottotitoli)
```
1
00:00:00,000 --> 00:00:03,500
Primo segmento di testo

2
00:00:03,500 --> 00:00:07,200
Secondo segmento di testo
```

## 🌍 Lingue Supportate

Il plugin supporta oltre 99 lingue tramite Whisper API. Alcune delle principali:

| Lingua | Codice | Lingua | Codice |
|--------|--------|--------|--------|
| Italiano | `it` | Inglese | `en` |
| Francese | `fr` | Tedesco | `de` |
| Spagnolo | `es` | Portoghese | `pt` |
| Russo | `ru` | Giapponese | `ja` |
| Cinese | `zh` | Arabo | `ar` |
| Hindi | `hi` | Coreano | `ko` |

Usa `"auto"` per il rilevamento automatico della lingua.

## 🎵 Formati Audio Supportati

- **MP3** (.mp3) - Più comune
- **WAV** (.wav) - Alta qualità
- **M4A** (.m4a) - Apple/iTunes
- **FLAC** (.flac) - Lossless
- **OGG** (.ogg) - Open source
- **WebM** (.webm) - Web
- **MP4** (.mp4) - Video con audio
- **MPEG** (.mpeg, .mpga) - Standard

**Limite dimensione**: 25MB per file

## 🔧 Integrazione con Altri Plugin

### Con Text-to-Speech (Pipeline Completa)
```yaml
states:
  # Trascrivi audio esistente
  transcribe:
    state_type: "speech_to_text"
    api_key: "{OPENAI_API_KEY}"
    audio_file: "input.mp3"
    output: "original_text"
    transition: "process_text"
  
  # Processa il testo
  process_text:
    state_type: "command"
    action:
      eval: "variables['processed_text'] = original_text['text'].upper()"
    transition: "generate_speech"
  
  # Genera nuovo audio
  generate_speech:
    state_type: "text_to_speech"
    api_key: "{ELEVENLABS_API_KEY}"
    text: "{processed_text}"
    output: "new_audio"
    transition: "end"
```

### Con LLM Agent (Analisi Testo)
```yaml
states:
  transcribe:
    state_type: "speech_to_text"
    api_key: "{OPENAI_API_KEY}"
    audio_file: "meeting.mp3"
    output: "meeting_transcript"
    transition: "analyze_meeting"
  
  analyze_meeting:
    state_type: "llm_agent"
    provider: "openai"
    api_key: "{OPENAI_API_KEY}"
    model: "gpt-4"
    prompt: |
      Analizza questa trascrizione di meeting e crea un riassunto:
      
      {meeting_transcript[text]}
      
      Fornisci:
      1. Punti chiave discussi
      2. Decisioni prese
      3. Action items
    output: "meeting_summary"
    transition: "send_summary"
```

### Con Telegram Bot (Trascrizione Messaggi Vocali)
```yaml
states:
  transcribe_voice_message:
    state_type: "speech_to_text"
    api_key: "{OPENAI_API_KEY}"
    audio_file: "{voice_message_path}"
    language: "it"
    output: "voice_transcription"
    transition: "send_transcription"
  
  send_transcription:
    state_type: "telegram"
    bot_token: "{TELEGRAM_BOT_TOKEN}"
    chat_id: "{chat_id}"
    message: |
      🎤 Trascrizione messaggio vocale:
      
      "{voice_transcription[text]}"
      
      📊 Dettagli:
      - Durata: {voice_transcription[file_info][size_mb]} MB
      - Parole: {voice_transcription[word_count]}
      - Tempo elaborazione: {voice_transcription[processing_time]}s
    transition: "end"
```

## 🛡️ Gestione Errori

Il plugin gestisce automaticamente diversi tipi di errori:

### Errori Comuni
- **File non trovato**: Verifica il percorso del file
- **Formato non supportato**: Usa formati audio supportati
- **File troppo grande**: Limite 25MB per file
- **API key invalida**: Verifica la chiave OpenAI
- **Quota esaurita**: Controlla i limiti del tuo account OpenAI

### Esempio Gestione Errori
```yaml
states:
  transcribe_with_fallback:
    state_type: "speech_to_text"
    api_key: "{OPENAI_API_KEY}"
    audio_file: "{audio_file}"
    output: "transcription_result"
    success_transition: "process_success"
    error_transition: "handle_transcription_error"
  
  handle_transcription_error:
    state_type: "if"
    condition: "'File troppo grande' in transcription_result.get('error', '')"
    true_state: "split_audio_file"
    false_state: "log_error_and_continue"
  
  split_audio_file:
    state_type: "command"
    action:
      eval: "print('File troppo grande, implementare splitting')"
    transition: "end"
  
  log_error_and_continue:
    state_type: "command"
    action:
      eval: "print(f'Errore trascrizione: {transcription_result[error]}')"
    transition: "end"
```

## 📈 Performance e Ottimizzazioni

### Tempi di Elaborazione Tipici
- **1 minuto di audio**: 2-5 secondi
- **5 minuti di audio**: 8-15 secondi
- **10 minuti di audio**: 15-30 secondi

### Consigli per Ottimizzare
1. **Usa formati compressi** (MP3) per file grandi
2. **Specifica la lingua** se conosciuta (più veloce dell'auto-detect)
3. **Usa temperature basse** (0.0-0.2) per trascrizioni precise
4. **Batch processing** per più file
5. **Workspace locale** per file temporanei

## 🔒 Sicurezza

- **Nessuna esecuzione codice**: Il plugin non esegue codice arbitrario
- **Validazione input**: Controllo formato e dimensione file
- **Cleanup automatico**: Rimozione file temporanei
- **API sicura**: Usa solo API OpenAI ufficiali

## 🐛 Troubleshooting

### Problema: "Libreria 'openai' non installata"
```bash
pip install openai>=1.0.0
```

### Problema: "API key invalida"
```bash
export OPENAI_API_KEY="sk-your-actual-api-key"
```

### Problema: "File troppo grande"
- Comprimi il file audio
- Usa formati più efficienti (MP3 vs WAV)
- Implementa chunking per file > 25MB

### Problema: "Formato non supportato"
- Converti in formato supportato
- Verifica estensione file
- Controlla Content-Type per URL

## 📞 Supporto

- **Issues**: [GitHub Issues](https://github.com/kuduk/intellyhub-plugins/issues)
- **Discussioni**: [GitHub Discussions](https://github.com/kuduk/intellyhub-plugins/discussions)
- **Email**: support@intellyhub.com

## 📄 Licenza

MIT License - Vedi file LICENSE per dettagli.

---

**Creato con ❤️ dal team IntellyHub**
