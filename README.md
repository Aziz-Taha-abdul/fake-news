# Fake News Detection Web Application

## Overview
This project is a full-stack web application for detecting fake news headlines using machine learning. It features a professional, classic UI and a backend powered by a Random Forest classifier trained on real news datasets.

---

## 1. Prerequisites
- **Python 3.8+** (recommend 3.10+)
- **pip** (Python package manager)
- (Optional) **virtualenv** for isolated environments

---

## 2. Setup Instructions

### a. Unzip the Project
Extract the zip file to a folder, e.g., `cloude/`.

### b. Set Up a Virtual Environment (Recommended)
Open a terminal in the project folder and run:
```sh
python -m venv .venv
```
Activate the environment:
- **Windows:**
  ```sh
  .venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```sh
  source .venv/bin/activate
  ```

### c. Install Dependencies
```sh
pip install -r requirements.txt
```

### d. Download NLTK Data (First Time Only)
The training script will attempt to download required NLTK data automatically. If you see errors, run this in Python:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

---

## 3. Train the Model
Run the training script to preprocess the data and train the model:
```sh
python train_model.py
```
- This will read the datasets in `models/True.csv` and `models/Fake.csv`, train the model, and save `model.pkl` and `vectorizer.pkl` in the `models/` folder.
- The script will print accuracy and other metrics.

---

## 4. Run the Web Application
Start the Flask server:
```sh
python app.py
```
- The app will be available at [http://localhost:5000](http://localhost:5000)
- Open this URL in your browser.

---

## 5. Using the App
- Enter a news headline in the input box and click **Analyze** to check if it’s likely real or fake.
- The **Live News Analysis** section shows real-time predictions for current news headlines.

---

## 6. Notes
- If you want to retrain the model with new data, update `models/True.csv` and `models/Fake.csv` and rerun `python train_model.py`.
- If you encounter errors about missing packages, ensure you’ve activated the virtual environment and installed all requirements.

---

## 7. Project Structure
- `app.py` – Flask backend
- `train_model.py` – Model training script
- `model.py` – Model loading and prediction logic
- `news_fetcher.py` – Live news fetching
- `requirements.txt` – Python dependencies
- `static/` – CSS and JS files
- `templates/` – HTML templates
- `models/` – Datasets and saved model/vectorizer

---

## 8. Troubleshooting
- If you see errors about missing NLTK data, run the download commands in a Python shell.
- For any other issues, ensure all dependencies are installed and the correct Python version is used.

---

Enjoy using the Fake News Detection Web App!
