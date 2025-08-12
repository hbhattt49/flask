from transformers import BertTokenizer, BertForSequenceClassification, pipeline

MODEL_DIR = "/absolute/path/to/your_model_dir"  # contains tf_model.h5, config.json, tokenizer files

# 1) Load PyTorch model from TF weights
model = BertForSequenceClassification.from_pretrained(
    MODEL_DIR,
    from_tf=True,
    low_cpu_mem_usage=False,   # ensures real tensors (avoids meta-tensors)
)

# 2) Load tokenizer and set a safe max length
tokenizer = BertTokenizer.from_pretrained(MODEL_DIR)
# Use the model’s max positions (BERT = 512)
tokenizer.model_max_length = min(getattr(tokenizer, "model_max_length", 512),
                                 getattr(model.config, "max_position_embeddings", 512))

# 3) Build the pipeline (CPU: device=-1; GPU: device=0)
self._model = pipeline(
    task="text-classification",
    model=model,
    tokenizer=tokenizer,
    device=-1,                # set 0 for CUDA:0
    return_all_scores=True    # get full distribution; pick top later
)


scores = self._model("Service was great, delivery slow", truncation=True, max_length=tokenizer.model_max_length)
# scores -> list of {"label": "...", "score": float}
best = max(scores, key=lambda x: x["score"])
print(best["label"], best["score"])


texts = ["Love it", "Hate it", "Meh."]
batch_scores = self._model(texts, truncation=True, padding=True, max_length=tokenizer.model_max_length)
# batch_scores -> list of lists
best_each = [max(s, key=lambda x: x["score"]) for s in batch_scores]
