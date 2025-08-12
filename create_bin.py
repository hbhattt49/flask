from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
tok = AutoTokenizer.from_pretrained("~/label-studio/model/BERT")
m = TFAutoModelForSequenceClassification.from_pretrained("~/label-studio/model/BERT", from_tf=True)
x = tok("sample text", return_tensors="tf")
print(m(**x).logits.numpy())




<View>
  <Header value="Text Classification"/>
  <Choices name="label" toName="text" choice="single" showInLine="true">
    <Choice value="Negative"/>
    <Choice value="Neutral"/>
    <Choice value="Positive"/>
  </Choices>
  <Text name="text" value="$text"/>
</View>
