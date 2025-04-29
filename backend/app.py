from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask import session
from datetime import timedelta

import numpy as np
import torch
import mlflow.pytorch
from transformers import AutoModelForSequenceClassification

from modeling.basic_functions import (
    tokenize,
)


# SECRET KEY
# TODO: SAFE IN ENVIRONMENT VARIABLE
import secrets
secret_key = secrets.token_hex(32)  # 64-character hexadecimal string


app = Flask(__name__)
app.secret_key = secret_key  # Replace with actual key
app.config.update(
    PERMANENT_SESSION_LIFETIME= timedelta(minutes=30),
    SESSION_COOKIE_SECURE=False, # only with HTTPS
    SESSION_COOKIE_SAMESITE='Lax',  # Allows cross-origin cookies
    SESSION_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_PATH='/',
)

CORS(app, resources={
    r"/predict": {
        "origins": "http://localhost:5173",
        "methods": ["POST","GET" "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True 
    }
})


def get_tokenized_text(txt):
    # x_tokenized = tokenize(txt, "microsoft/deberta-v3-base")
    x_tokenized = tokenize(txt, "kathixx/fallacy-deberta-model")
    # x_tokenized = tokenize(txt, "marbor/FallaSee")
    return x_tokenized

def predict(model, encodings, batch_size=8):
    # Set the model to evaluation mode
    model.eval()
    
    # Use GPU
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model.to(device)
    
    # Perform inference
    probabilities = []
    for i in range(0, len(encodings["input_ids"]), batch_size):
        with torch.no_grad():
            batch = {
                key: val[i:i+batch_size].to(device) 
                for key, val in encodings.items()
            }
            outputs = model(**batch)
            probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()
            probabilities.extend(probs)
            
        # Clear GPU memory after each batch
        torch.mps.empty_cache()
    
    return np.array(probabilities)

def get_label(label):
    if label == 0:
        return 'ad_hominem'
    if label == 1:
        return 'appeal to authority'
    if label == 2:
        return 'appeal to emotion'
    if label == 3:
        return 'false dilemma'
    if label == 4:
        return 'none'
    if label == 5:
        return 'slippery slope'

def get_first_prediction(proba):
    pred = np.argmax(proba, axis=1)
    pred_int = int(pred[0])
    proba = proba[np.arange(len(pred)), pred]
    proba_int = float(proba[0])
    return pred_int, proba_int

def get_second_prediction(proba):
    pred = np.argsort(proba, axis=1)[:, -2] 
    pred_int = int(pred[0])
    proba = np.sort(proba, axis=1)[:, -2]
    proba_int = float(proba[0])
    return pred_int, proba_int

@app.after_request
def after_request(response):
    # Add CORS headers for every response
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'  # Replace with your client domain
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


@app.route('/predict', methods=['POST'])
@cross_origin(origin='http://localhost:5173')
def input_predict_text():
    # model = mlflow.pytorch.load_model('./models/deberta_v3_multi_with_none_large_3_epochs/pytorch_model')
    # model = AutoModelForSequenceClassification.from_pretrained("marbor/FallaSee")

    model = AutoModelForSequenceClassification.from_pretrained("kathixx/fallacy-deberta-model")

    #get input
    txt = request.get_json()['txt']
    tokenized_txt = get_tokenized_text(txt)
    probabilities = predict(model, tokenized_txt)
    print('All probabilites:', probabilities)
    return jsonify({
        '0_ad_hominem': float(probabilities[0][0]),
        '1_authority': float(probabilities[0][1]),
        '2_emotion': float(probabilities[0][2]),
        '3_dilemma': float(probabilities[0][3]),
        '4_none': float(probabilities[0][4]),
        '5_slope': float(probabilities[0][5])
        })

if __name__ == "__main__":
    app.run(debug=True)

