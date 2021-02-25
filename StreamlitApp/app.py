import streamlit as st
from transformers import BertForSequenceClassification, BertConfig, Trainer,BertTokenizer
import torch
import requests
import json



class CovidDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


def main():
    st.title("Sentence Classifier")
    sentence = st.text_input("Type a sentence")
    tokenizer_bert = BertTokenizer.from_pretrained("bert-base-uncased")
    test_encodings = tokenizer_bert([sentence], truncation=True, padding=True)
    X_test = CovidDataset(test_encodings, [0])
    config = BertConfig.from_json_file('./model/config.json')
    model = BertForSequenceClassification.from_pretrained('./model/', config=config)
    trainer = Trainer(
        model=model,
    )

    result = trainer.predict(test_dataset=X_test).predictions.argmax(-1)
    if (result[0] == 0 and sentence != ''):
        st.write("The sentence does not seem suspicious.")
    elif (sentence != '' and result[0] == 1):
        st.write("The sentence seems suspicious.")
        query = "https://factchecktools.googleapis.com/v1alpha1/claims:search?query={}&key=AIzaSyCDkPw22qbilLXdoQFey-JHfVv0MP5_Hhw".format(sentence.replace(' ', '%20'))
        r =requests.get(query)
        if r.text:
          st.write('Similar fact-checked claims found:')
          for claim in json.loads(r.text)['claims']:
            st.write('- Title: ' + claim['text'] + '; Rating: ' + claim['claimReview'][0]['textualRating'])

main()