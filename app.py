import os
from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold, GridSearchCV

app = Flask(__name__)

model = None
accuracy = "N/A"

def train_decision_tree():
    global model, accuracy
    
    # Use absolute path to ensure Vercel finds dataR2.csv
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(base_dir, 'dataR2.csv')
    
    if not os.path.exists(csv_file):
        print(f"\n[!] ERROR: '{csv_file}' was not found.\n")
        return

    df = pd.read_csv(csv_file)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={'MCP.1': 'MCP1', 'MCP-1': 'MCP1'})
    
    if 'Classification' in df.columns:
        df['Classification'] = df['Classification'].map({1: 0, 2: 1})
    
    X = df[['Age', 'BMI', 'Glucose', 'Insulin', 'HOMA', 'Leptin', 'Adiponectin', 'Resistin', 'MCP1']]
    y = df['Classification']

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    param_grid = {
        'max_depth': [3, 4, 5, 6],
        'criterion': ['gini', 'entropy'],
        'min_samples_split': [2, 4, 6],
        'min_samples_leaf': [1, 2, 3]
    }

    grid_search = GridSearchCV(
        estimator=DecisionTreeClassifier(random_state=42),
        param_grid=param_grid,
        cv=cv,
        scoring='accuracy',
        n_jobs=-1
    )

    grid_search.fit(X, y)

    best_cv_accuracy = round(grid_search.best_score_ * 100, 1)
    accuracy = f"{best_cv_accuracy}%"
    model = grid_search.best_estimator_

train_decision_tree()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/detector')
def detector():
    return render_template('index.html', accuracy=accuracy)

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model is not trained. Ensure dataR2.csv is present.'}), 500

    try:
        data = request.json
        input_features = [
            float(data['Age']),
            float(data['BMI']),
            float(data['Glucose']),
            float(data['Insulin']),
            float(data['HOMA']),
            float(data['Leptin']),
            float(data['Adiponectin']),
            float(data['Resistin']),
            float(data['MCP1'])
        ]

        prediction = int(model.predict([input_features])[0])
        confidence = round(model.predict_proba([input_features])[0][prediction] * 100, 1)

        return jsonify({
            'prediction': prediction,
            'confidence': confidence
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
