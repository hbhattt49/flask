from label_studio_ml.model import LabelStudioMLBase
from transformers import pipeline

class SimpleTextClassifier(LabelStudioMLBase):
    def __init__(self, **kwargs):
        super(SimpleTextClassifier, self).__init__(**kwargs)
        self.classifier = pipeline("sentiment-analysis")

    def predict(self, tasks, **kwargs):
        predictions = []
        for task in tasks:
            text = task['data']['text']
            result = self.classifier(text)[0]
            label = result['label'].capitalize()  # Convert to match your labels

            predictions.append({
                "result": [{
                    "from_name": "label",
                    "to_name": "text",
                    "type": "choices",
                    "value": {
                        "choices": [label]
                    }
                }],
                "score": result['score']
            })
        return predictions





[
  {"data": {"text": "The product quality is excellent and exceeded my expectations!"}},
  {"data": {"text": "I am really disappointed with the service I received."}},
  {"data": {"text": "It’s okay, nothing extraordinary but not bad either."}},
  {"data": {"text": "Absolutely fantastic experience, will buy again!"}},
  {"data": {"text": "The delivery was late and the packaging was damaged."}},
  {"data": {"text": "Customer support was helpful and resolved my issue quickly."}},
  {"data": {"text": "This is the worst app I have ever used."}},
  {"data": {"text": "Neutral feedback — just wanted to try it out."}},
  {"data": {"text": "Pretty decent value for money."}},
  {"data": {"text": "It crashed multiple times, very frustrating experience."}}
]




<View>
  <Labels name="label" toName="text">
    <Label value="Positive" background="green"/>
    <Label value="Negative" background="red"/>
    <Label value="Neutral" background="blue"/>
  </Labels>
  <Text name="text" value="$text"/>
</View>







import requests

headers = {
    "Authorization": "Token your_actual_api_key"
}

res = requests.get("http://localhost:8080/api/current-user", headers=headers)

print(res.status_code, res.text)
