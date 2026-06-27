import os
import glob
import json
import logging
import numpy as np
import onnxruntime as ort
import sentencepiece as spm
from flask import Flask, request, Response, render_template
from flask_cors import CORS

# Configurazione Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configurazioni Modello
MODEL_ONNX_PATH = os.getenv("MODEL_ONNX_PATH", "./model/emma5.onnx")
TOKENIZER_PATH = os.getenv("TOKENIZER_PATH", "./model/bpe.model")
GPU_MEM_LIMIT = int(os.getenv("GPU_MEM_LIMIT", 6 * 1024 * 1024 * 1024))  # 6GB default
MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", 512))

# Setup NVIDIA Paths
venv_nvidia_path = os.path.join(os.path.dirname(__file__), "venv", "Lib", "site-packages", "nvidia")
if os.path.exists(venv_nvidia_path):
    nvidia_bins = glob.glob(os.path.join(venv_nvidia_path, "*", "bin"))
    for bin_path in nvidia_bins:
        if hasattr(os, 'add_dll_directory'):
            try:
                os.add_dll_directory(bin_path)
            except OSError as e:
                logger.warning(f"Impossibile aggiungere la directory DLL {bin_path}: {e}")
        os.environ["PATH"] = bin_path + os.pathsep + os.environ["PATH"]


class DilemmaModel:
    """Classe manager per gestire il caricamento e l'inferenza del modello Dilemma-5."""
    
    def __init__(self):
        self.tokenizer = None
        self.session = None

    def load(self):
        logger.info("Caricamento del tokenizer...")
        if not os.path.exists(TOKENIZER_PATH):
            raise FileNotFoundError(f"Tokenizer non trovato in {TOKENIZER_PATH}")
        self.tokenizer = spm.SentencePieceProcessor(model_file=TOKENIZER_PATH)
        
        logger.info("Inizializzazione sessione ONNX (CUDA/CPU)...")
        if not os.path.exists(MODEL_ONNX_PATH):
            raise FileNotFoundError(f"Modello ONNX non trovato in {MODEL_ONNX_PATH}")

        providers = [
            ('CUDAExecutionProvider', {
                'device_id': 0,
                'arena_extend_strategy': 'kNextPowerOfTwo',
                'gpu_mem_limit': GPU_MEM_LIMIT,
                'cudnn_conv_algo_search': 'EXHAUSTIVE',
                'do_copy_in_default_stream': True,
            }),
            'CPUExecutionProvider',
        ]
        
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        try:
            self.session = ort.InferenceSession(MODEL_ONNX_PATH, sess_options=session_options, providers=providers)
            logger.info("Modello caricato con successo.")
        except Exception as e:
            logger.error(f"Errore durante il caricamento del modello ONNX: {e}")
            raise

    def generate_response(self, prompt: str, max_new_tokens: int = 150, temperature: float = 0.7, top_k: int = 40, repetition_penalty: float = 1.3):
        if not self.tokenizer or not self.session:
            raise RuntimeError("Il modello non è stato caricato.")

        input_ids = [self.tokenizer.bos_id()] + self.tokenizer.encode_as_ids(prompt)
        generated_text = ""
        
        for _ in range(max_new_tokens):
            if len(input_ids) >= MAX_CONTEXT_LENGTH:
                logger.warning("Raggiunto il limite massimo di contesto.")
                break
                
            inputs = np.array([input_ids], dtype=np.int64)
            outputs = self.session.run(None, {"input_ids": inputs})
            logits = outputs[0][0, -1, :].copy()
            
            # --- Repetition Penalty (senza di questo al modello piace ripetersi) ---
            if repetition_penalty > 1.0:
                for token_id in set(input_ids):
                    if logits[token_id] < 0:
                        logits[token_id] *= repetition_penalty
                    else:
                        logits[token_id] /= repetition_penalty
                    
            # --- Temperature & Sampling ---
            if temperature > 0.0:
                logits = logits / temperature
                
            if top_k > 0:
                k_th_value = np.sort(logits)[-top_k]
                logits[logits < k_th_value] = -float('Inf')
                
            exp_logits = np.exp(logits - np.max(logits))
            probs = exp_logits / np.sum(exp_logits)
            
            if temperature > 0.0 or top_k > 0:
                next_token_id = int(np.random.choice(len(probs), p=probs))
            else:
                next_token_id = int(np.argmax(probs))
            
            if next_token_id == self.tokenizer.eos_id():
                break
                
            input_ids.append(next_token_id)
            
            new_generated_text = self.tokenizer.decode_ids(input_ids[len(self.tokenizer.encode_as_ids(prompt))+1:])
            delta = new_generated_text[len(generated_text):]
            
            if delta:
                generated_text = new_generated_text
                yield delta


app = Flask(__name__)
CORS(app)
dilemma_model = DilemmaModel()

@app.route("/api/status", methods=["GET"])
def status():
    if dilemma_model.session is None:
        return {"error": "Modello non ancora caricato"}, 503
        
    active_providers = dilemma_model.session.get_providers()
    is_cuda_active = 'CUDAExecutionProvider' in active_providers
    
    return {
        "cuda_active": is_cuda_active,
        "primary_provider": active_providers[0] if active_providers else "Unknown"
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    if not data or not data.get("message"):
        return {"error": "Messaggio mancante"}, 400
        
    user_input = data["message"].strip()
    prompt = f"### Istruzione:\n{user_input}\n\n### Risposta:\n"
    
    def stream():
        try:
            for chunk in dilemma_model.generate_response(prompt):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Errore durante la generazione: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
    return Response(stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    try:
        dilemma_model.load()
    except Exception as e:
        logger.critical(f"Impossibile avviare il modello: {e}")
        exit(1)
        
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=False)