from transformers import AutoTokenizer, TFAutoModelForSequenceClassification, AutoModelForSequenceClassification

MODEL_DIR = "/opt/models/my-bert"

# 1) Load TF model
tf_model = TFAutoModelForSequenceClassification.from_pretrained(MODEL_DIR, from_tf=True)

# 2) Save as PyTorch
tf_model.save_pretrained(MODEL_DIR, saved_model=False)

# 3) Save tokenizer (optional if already there)
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
tokenizer.save_pretrained(MODEL_DIR)
