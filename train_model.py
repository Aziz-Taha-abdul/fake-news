import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, classification_report
from sklearn.utils import shuffle

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Load True.csv and Fake.csv from the models directory
true_path = os.path.join('models', 'True.csv')
fake_path = os.path.join('models', 'Fake.csv')
df_true = pd.read_csv(true_path)
df_fake = pd.read_csv(fake_path)
df_true['label'] = 'REAL'
df_fake['label'] = 'FAKE'

# Use 'title' column for training (adjust if needed)
df_true['text'] = df_true['title']
df_fake['text'] = df_fake['title']

df = pd.concat([df_true, df_fake], ignore_index=True)

# Shuffle data
df = shuffle(df, random_state=42)

# Filter out very short headlines (less than 3 words)
df = df[df['text'].str.split().str.len() >= 3]
print(f"Number of samples after filtering short headlines: {len(df)}")
if len(df) == 0:
    print("No data left after filtering. Please check your dataset or lower the minimum word count.")
    exit(1)

def preprocess(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = nltk.word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return ' '.join(tokens)

df['processed'] = df['text'].apply(preprocess)
X = df['processed']
y = df['label'].map({'FAKE': 0, 'REAL': 1})

vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1,2))
X_vec = vectorizer.fit_transform(X)

# Split data for evaluation
X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42, stratify=y)

model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print('Accuracy:', accuracy_score(y_test, y_pred))
print('Precision:', precision_score(y_test, y_pred))
print('Recall:', recall_score(y_test, y_pred))
print('Confusion Matrix:\n', confusion_matrix(y_test, y_pred))
print('Classification Report:\n', classification_report(y_test, y_pred, target_names=['FAKE', 'REAL']))

# Print top 20 feature importances
import numpy as np
feature_names = np.array(vectorizer.get_feature_names_out())
importances = model.feature_importances_
indices = np.argsort(importances)[-20:][::-1]
print("Top 20 important features:")
for idx in indices:
    print(f"{feature_names[idx]}: {importances[idx]:.4f}")

# Save model and vectorizer
with open('models/vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
with open('models/model.pkl', 'wb') as f:
    pickle.dump(model, f)
