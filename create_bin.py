from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
tok = AutoTokenizer.from_pretrained("~/label-studio/model/BERT")
m = TFAutoModelForSequenceClassification.from_pretrained("~/label-studio/model/BERT", from_tf=True)
x = tok("sample text", return_tensors="tf")
print(m(**x).logits.numpy())



from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_DIR = "/path/to/your_model_dir"

# Load TF model into PyTorch
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR, from_tf=True)

# Save as PyTorch model
model.save_pretrained(MODEL_DIR)

# Ensure tokenizer is saved
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
tokenizer.save_pretrained(MODEL_DIR)

print("✅ Conversion complete. pytorch_model.bin is now in", MODEL_DIR)






# TF-only Label Studio backend that loads model in setup()
from typing import List, Dict, Any
import tensorflow as tf
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from label_studio_ml.model import LabelStudioMLBase

class BertTextClassifierTF(LabelStudioMLBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_dir = getattr(self, "model_dir", None) or kwargs.get("model_dir") or "./"

        # Defer heavy loads to setup()
        self.tokenizer = None
        self.model = None

        # Filled in setup()
        self.labels: List[str] = []
        self.model_label_order: List[str] = []
        self.model_to_ls_idx: Dict[str, int] = {}
        self.from_name = "label"  # <Choices name="...">
        self.to_name = "text"     # <Text name="...">

    def _ensure_loaded(self):
        if self.tokenizer is None:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir, use_fast=True)
        if self.model is None:
            # IMPORTANT: no torch-only kwargs here
            self.model = TFAutoModelForSequenceClassification.from_pretrained(
                self.model_dir, from_tf=True
            )

            # Build label order from model config if present
            id2label = getattr(self.model.config, "id2label", None)
            if id2label:
                try:
                    ordered = [id2label[str(i)] for i in range(len(id2label))]
                except KeyError:
                    ordered = [id2label[i] for i in range(len(id2label))]
                self.model_label_order = ordered
            elif not self.model_label_order:
                # fallback if setup() hasn’t run yet
                n = int(getattr(self.model.config, "num_labels", 2))
                self.model_label_order = [f"LABEL_{i}" for i in range(n)]

            if not self.labels:
                # fallback labels if setup() hasn't filled them
                self.labels = self.model_label_order
                self.model_to_ls_idx = {name: i for i, name in enumerate(self.labels)}

    def setup(self):
        """Called by Label Studio via /setup with the project label config."""
        # Parse controls from label config
        for name, info in self.parsed_label_config.items():
            if info.get("type") == "Choices":
                self.from_name = name
                self.labels = info.get("labels", [])
                # Usually a list with one target name (e.g., ['text'])
                tos = info.get("to_name") or []
                if tos:
                    self.to_name = tos[0]
                break

        # Load tokenizer/model now so predict won’t see None
        self._ensure_loaded()

        # Map model label names to LS labels
        self.model_to_ls_idx = {name: i for i, name in enumerate(self.labels)} or {
            name: i for i, name in enumerate(self.model_label_order)
        }

        return {"status": "ok", "labels": self.labels, "from_name": self.from_name, "to_name": self.to_name}

    def _predict_one(self, text: str) -> Dict[str, Any]:
        self._ensure_loaded()

        toks = self.tokenizer(
            text,
            return_tensors="tf",
            truncation=True,
            padding="longest",
            max_length=512,
        )
        outputs = self.model(**toks)
        probs = tf.nn.softmax(outputs.logits, axis=-1).numpy().reshape(-1)

        scored = []
        for idx_in_model, label_name in enumerate(self.model_label_order):
            ls_idx = self.model_to_ls_idx.get(label_name)
            if ls_idx is not None:
                label = self.labels[ls_idx] if self.labels else label_name
                scored.append((label, float(probs[idx_in_model])))

        scored.sort(key=lambda x: x[1], reverse=True)
        top_label, top_score = scored[0]

        return {
            "result": [{
                "from_name": self.from_name,
                "to_name": self.to_name,
                "type": "choices",
                "value": {"choices": [top_label]},
                "score": top_score
            }],
            "scores": {k: v for k, v in scored},
            "model_version": getattr(self.model.config, "_name_or_path", "tf-model"),
        }

    def predict(self, tasks: List[Dict], **kwargs) -> List[Dict]:
        predictions = []
        for task in tasks:
            text = task.get("data", {}).get(self.to_name) or task.get("data", {}).get("text", "")
            predictions.append(self._predict_one(text))
        return predictions
