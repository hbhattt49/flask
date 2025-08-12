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
