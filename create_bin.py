import os
import json
from pathlib import Path
from transformers import (
    AutoConfig, AutoTokenizer,
    AutoModelForSequenceClassification,   # PyTorch
    logging
)

logging.set_verbosity_info()

MODEL_DIR = Path("/opt/models/my-bert")  # <-- change to your path

def ensure_labels(cfg_path: Path):
    """
    Make sure id2label/label2id exist in config.json.
    If missing, create a default mapping 0..num_labels-1 -> LABEL_{i}.
    """
    cfg = json.loads(cfg_path.read_text())
    num_labels = cfg.get("num_labels")
    if num_labels is None:
        # Best effort: for many BERT cls heads this is present. If not, assume 2.
        num_labels = 2
        cfg["num_labels"] = num_labels

    if "id2label" not in cfg or "label2id" not in cfg:
        id2label = {str(i): f"LABEL_{i}" for i in range(num_labels)}
        label2id = {v: int(k) for k, v in id2label.items()}
        cfg["id2label"] = id2label
        cfg["label2id"] = label2id
        cfg_path.write_text(json.dumps(cfg, indent=2))
        print(f"[info] Added default id2label/label2id to {cfg_path}")
    else:
        print("[info] id2label/label2id already present")

def main():
    assert MODEL_DIR.exists(), f"Model dir not found: {MODEL_DIR}"

    cfg_path = MODEL_DIR / "config.json"
    assert cfg_path.exists(), "config.json missing"

    # Make sure tokenizer artifacts exist; if not, try to create from whatever is there.
    tok_files = ["vocab.txt", "tokenizer.json", "tokenizer_config.json"]
    if not any((MODEL_DIR / f).exists() for f in tok_files):
        raise FileNotFoundError("No tokenizer files found (vocab.txt/tokenizer.json).")

    # Ensure labels in config (helps LS alignment)
    ensure_labels(cfg_path)

    # Load config (to display helpful info)
    cfg = AutoConfig.from_pretrained(MODEL_DIR)
    print("[info] architectures:", getattr(cfg, "architectures", None))
    print("[info] num_labels:", getattr(cfg, "num_labels", None))

    # Save tokenizer (normalizes files)
    tok = AutoTokenizer.from_pretrained(MODEL_DIR, use_fast=True)
    tok.save_pretrained(MODEL_DIR)

    # --- Attempt 1: load TF checkpoint into a PyTorch model ---
    torch_model_path = MODEL_DIR / "pytorch_model.bin"
    if torch_model_path.exists():
        print("[info] pytorch_model.bin already exists; nothing to do.")
        return

    loaded = False
    try:
        print("[info] Trying TF -> Torch (from_tf=True) ...")
        pt_model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_DIR, from_tf=True
        )
        pt_model.save_pretrained(MODEL_DIR)
        loaded = True
        print("[success] Converted TF weights to PyTorch.")
    except TypeError as e:
        # This specific error happens if the class doesn’t accept from_tf,
        # or you resolved to a TF class by mistake (rare with AutoModel*).
        print(f"[warn] TypeError during TF load: {e}")
    except Exception as e:
        print(f"[warn] Generic error during TF load: {e}")

    # --- Attempt 2: load Flax checkpoint into a PyTorch model ---
    if not loaded and (MODEL_DIR / "flax_model.msgpack").exists():
        try:
            print("[info] Trying Flax -> Torch (from_flax=True) ...")
            pt_model = AutoModelForSequenceClassification.from_pretrained(
                MODEL_DIR, from_flax=True
            )
            pt_model.save_pretrained(MODEL_DIR)
            loaded = True
            print("[success] Converted Flax weights to PyTorch.")
        except Exception as e:
            print(f"[warn] Error during Flax load: {e}")

    if not loaded:
        raise RuntimeError(
            "Could not produce PyTorch weights. "
            "Ensure either tf_model.h5 (TF) or flax_model.msgpack (Flax) is present, "
            "and the model is a *sequence classification* architecture."
        )

if __name__ == "__main__":
    main()
