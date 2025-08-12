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







from typing import List, Dict, Any
import numpy as np
import tensorflow as tf
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from label_studio_ml.model import LabelStudioMLBase


class BertTextClassifierTF(LabelStudioMLBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Extract labels from the project config
        choice_name = None
        for name, info in self.parsed_label_config.items():
            if info.get("type") == "Choices":
                choice_name = name
                break
        if not choice_name:
            raise RuntimeError("No <Choices> control found in label config.")

        self.labels: List[str] = self.parsed_label_config[choice_name]["labels"]

        # Model dir provided by LS backend CLI
        self.model_dir = getattr(self, "model_dir", None) or kwargs.get("model_dir") or "./"

        # Load tokenizer and TF model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir, use_fast=True)
        self.model = TFAutoModelForSequenceClassification.from_pretrained(
            self.model_dir,
            from_tf=True
        )

        # Handle id2label mappings safely
        id2label = getattr(self.model.config, "id2label", None)
        if id2label:
            try:
                ordered = [id2label[str(i)] for i in range(len(id2label))]
            except KeyError:
                ordered = [id2label[i] for i in range(len(id2label))]
            self.model_label_order = ordered
        else:
            self.model_label_order = self.labels

        self.model_to_ls_idx = {name: i for i, name in enumerate(self.labels)}

    def _predict_one(self, text: str) -> Dict[str, Any]:
        toks = self.tokenizer(
            text,
            return_tensors="tf",
            truncation=True,
            padding="longest",
            max_length=512,
        )
        outputs = self.model(**toks)
        probs = tf.nn.softmax(outputs.logits, axis=-1).numpy().reshape(-1)

        scores = []
        for idx_in_model, label_name in enumerate(self.model_label_order):
            ls_idx = self.model_to_ls_idx.get(label_name, None)
            if ls_idx is not None:
                scores.append((self.labels[ls_idx], float(probs[idx_in_model])))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_label, top_score = scores[0]

        return {
            "result": [{
                "from_name": "label",  # must match <Choices name="label">
                "to_name": "text",     # must match <Text name="text">
                "type": "choices",
                "value": {"choices": [top_label]},
                "score": top_score
            }],
            "scores": {k: v for k, v in scores},
            "model_version": getattr(self.model.config, "_name_or_path", "tf-model"),
        }

    def predict(self, tasks: List[Dict], **kwargs) -> List[Dict]:
        predictions = []
        for task in tasks:
            text = task["data"].get("text", "")
            predictions.append(self._predict_one(text))
        return predictions
