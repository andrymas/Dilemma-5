# Dilemma-5 Local Web UI

Una semplice, ma elegante interfaccia web per eseguire localmente il modello (da noi ribattezzato) **Dilemma-5** utilizzando **ONNX Runtime** con accelerazione **CUDA GPU** o **CPU**.
L'obiettivo di questo progetto è garantire l'ormai celebre e tanto acclamata **"sovranità digitale"** (un ringraziamento speciale alle grandi dichiarazioni del CEO dell'azienda originaria). Ora puoi testare con mano i *fantastici* risultati del modello direttamente sul tuo PC, in totale privacy, e giudicare tu stesso.

---

## ⚠️ Disclaimer Legale Importante

**Questo progetto NON è affiliato, supportato, sponsorizzato o approvato dall'azienda creatrice del modello originale.**
Questa repository **NON contiene i pesi del modello** né alcun software proprietario dell'azienda creatrice. 

Il progetto è nato a puro scopo **satirico, di parodia e di ricerca indipendente**, e fornisce esclusivamente un'interfaccia grafica open-source per eseguire i modelli archiviati pubblicamente. Il modello originale citato è ospitato su Hugging Face al seguente indirizzo: [https://huggingface.co/eldavoo/emma-5](https://huggingface.co/eldavoo/emma-5). 

Qualsiasi marchio registrato o diritto d'autore citato (come "EMMA") appartiene esclusivamente ai rispettivi proprietari. L'autore di questa repository declina ogni responsabilità per un uso improprio del software o per eventuali violazioni delle licenze d'uso dei modelli caricati dall'utente.

---

## ✨ Caratteristiche
- **Sovranità Digitale**: Nessuna API esterna, tutto gira in locale.
- **Accelerazione Hardware**: Supporto nativo per **CUDA 12** per prestazioni ottimali su GPU NVIDIA. Ripiego automatico su CPU se la GPU non è disponibile.
- **Facilità d'Uso**: Basta avviare lo script `start.bat` per installare automaticamente tutte le dipendenze e avviare il server Flask.

## 🚀 Prerequisiti
- **OS:** Windows (per lo script `start.bat`)
- **Python:** 3.11 o superiore
- **Hardware (Opzionale ma consigliato):** GPU NVIDIA compatibile con CUDA per l'accelerazione hardware (minimo 6-8GB VRAM consigliati).

## 🛠️ Installazione e Utilizzo

1. **Clona questa repository** (o scarica lo zip):
   ```bash
   git clone https://github.com/andrymas/sovrano-digital.git
   cd sovrano-digital
   ```

2. **Scarica il modello:**
   Scarica i file del modello dal repository Hugging Face: [eldavoo/emma-5](https://huggingface.co/eldavoo/emma-5).
   - Crea una cartella chiamata `model` nella root del progetto.
   - Inserisci al suo interno il file ONNX (es. `emma5.onnx`) e il tokenizer (es. `bpe.model`).
   
   La struttura delle cartelle dovrà essere la seguente:
   ```text
   emma-local-ui/
   ├── model/
   │   ├── emma5.onnx
   │   └── bpe.model
   ├── static/
   ├── templates/
   ├── web_app.py
   ├── requirements.txt
   └── start.bat
   ```

3. **Avvia il server:**
   Fai doppio clic su `start.bat`. 
   Il file batch creerà automaticamente un ambiente virtuale isolato (`venv`), installerà le dipendenze dichiarate in `requirements.txt` (comprese le librerie CUDA 12 per ONNX) e avvierà il web server.

4. **Apri l'interfaccia:**
   Vai sul tuo browser e visita `http://localhost:5000`.

## 📜 Licenza
Questo progetto (l'interfaccia UI e gli script di avvio) è rilasciato sotto licenza MIT. 
Tuttavia, **il modello EMMA-5 è soggetto alla propria licenza**. Assicurati di leggere e rispettare i termini d'uso indicati nella pagina del modello su Hugging Face prima di scaricarlo o utilizzarlo.
