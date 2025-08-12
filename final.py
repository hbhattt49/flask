from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class MyClassifier:
    def __init__(self, model_dir_or_name):
        self.base = Path(model_dir_or_name) if Path(model_dir_or_name).exists() else model_dir_or_name
        self._ready = False

    def _lazy_init(self):
        if self._ready:
            return

        # 1) Load tokenizer (fast) and model (PyTorch only)
        self.tokenizer = AutoTokenizer.from_pretrained(self.base, use_fast=True)

        # IMPORTANT: do not use from_tf=True unless your folder ONLY has tf_model.h5
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.base,
            low_cpu_mem_usage=False,     # disable meta init
            device_map=None              # don’t let accelerate scatter it
        )

        # 2) Move to device AFTER weights are materialized
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device).eval()

        # 3) Sanity: make sure nothing is on meta
        if any(p.is_meta for p in self.model.parameters()):
            raise RuntimeError("Model still on meta device—loading arguments are wrong.")

        # 4) Label mapping
        cfg = self.model.config
        self.id2label = getattr(cfg, "id2label", None) or {i: f"LABEL_{i}" for i in range(cfg.num_labels)}

        self._ready = True

    @torch.inference_mode()
    def predict(self, texts):
        self._lazy_init()
        if isinstance(texts, str):
            texts = [texts]

        enc = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.tokenizer.model_max_length,
            return_tensors="pt"
        )
        enc = {k: v.to(self.device) for k, v in enc.items()}

        logits = self.model(**enc).logits
        probs = torch.softmax(logits, dim=-1)

        top_ids = probs.argmax(dim=-1).tolist()
        probs_list = probs.cpu().tolist()

        out = []
        for i, p in zip(top_ids, probs_list):
            out.append({
                "label": self.id2label[int(i)],
                "score": float(p[i]),
                "scores": [{"label": self.id2label[j], "score": float(p[j])} for j in range(len(p))]
            })
        return out
