from flask import Flask, request, jsonify
import numpy as np
import spacy
import tensorflow as tf
from tensorflow.keras import layers, models
from spacy.matcher import Matcher

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Define Matcher and patterns
matcher = Matcher(nlp.vocab)

pattern_requirement = [{"LOWER": "i'm"}, {"LOWER": "looking"}, {"LOWER": "for"}, {"POS": "DET", "OP": "?"}, {"POS": "NOUN"}]
matcher.add("REQUIREMENT", [pattern_requirement])

pattern_policy = [{"LOWER": "our"}, {"LOWER": "policy"}, {"LOWER": "is"}]
matcher.add("POLICY", [pattern_policy])

pattern_objection = [{"LOWER": "i"}, {"LOWER": "don't"}, {"LOWER": "like"}]
matcher.add("OBJECTION", [pattern_objection])

def extract_features(doc):
    """Extract features and matched patterns from spaCy doc."""
    features = {
        "num_adjectives": sum(1 for token in doc if token.pos_ == "ADJ"),
        "contains_money": any(ent.label_ == "MONEY" for ent in doc.ents),
        "num_nouns": sum(1 for token in doc if token.pos_ == "NOUN"),
        "has_requirements": 0,
        "has_policies": 0,
        "has_objections": 0
    }
    
    matches = matcher(doc)
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]
        if string_id == "REQUIREMENT":
            features["has_requirements"] = 1
        elif string_id == "POLICY":
            features["has_policies"] = 1
        elif string_id == "OBJECTION":
            features["has_objections"] = 1
    
    return features

def build_model(input_shape):
    """Build and compile the TensorFlow model."""
    model = models.Sequential([
        layers.Dense(16, activation='relu', input_shape=(input_shape,)),
        layers.Dense(8, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Load the model (for demonstration purposes, you should train or load an actual model)
model = build_model(6)  # Assuming 6 features

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')

    doc = nlp(text)
    features = extract_features(doc)

    X_test = np.array([[features["num_adjectives"], 
                        features["contains_money"], 
                        features["num_nouns"], 
                        features["has_requirements"], 
                        features["has_policies"], 
                        features["has_objections"]]])
    
    prediction = model.predict(X_test)
    prediction_label = (prediction > 0.5).astype(int)

    result = {
        'has_requirements': features['has_requirements'],
        'has_policies': features['has_policies'],
        'has_objections': features['has_objections'],
        'prediction': 'Objection' if prediction_label[0] else 'No Objection'
    }
    
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
