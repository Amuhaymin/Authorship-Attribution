import pandas as pd
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

def load_data(file_path, encodings=['utf-8', 'latin1', 'ISO-8859-1', 'cp1252']):
   for encoding in encodings:
       try:
           data = pd.read_csv(file_path, encoding=encoding)
           print(f"Data loaded successfully with encoding: {encoding}")
           return data
       except UnicodeDecodeError as e:
           print(f"Error loading data with {encoding}: {e}")
       except Exception as e:
           print(f"An error occurred with {encoding}: {e}")
   print("Failed to load data with all attempted encodings.")
   return None

def preprocess_text(text):
   text = text.lower()
   text = text.translate(str.maketrans('', '', string.punctuation))
   return text

# Load and preprocess the training data
train_file_path = 'dataset/Gungor_2018_VictorianAuthorAttribution_data-train.csv'
train_data = load_data(train_file_path)
if train_data is not None:
   train_data['processed_text'] = train_data['text'].apply(preprocess_text)

   # Split data into training (80%) and testing (20%)
   X = train_data['processed_text']
   y = train_data['author']
   X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

   # Initialize the TF-IDF Vectorizer
   tfidf_vectorizer = TfidfVectorizer(max_features=1000)
   X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
   X_test_tfidf = tfidf_vectorizer.transform(X_test)

   # Initialize and train the logistic regression model
   model = LogisticRegression(max_iter=1000)
   model.fit(X_train_tfidf, y_train)

   # Predict on the test set
   y_pred = model.predict(X_test_tfidf)

   # Evaluate the model
   accuracy = accuracy_score(y_test, y_pred)
   print(f"Accuracy: {accuracy * 100:.2f}%")
   print("\nClassification Report:")
   print(classification_report(y_test, y_pred))
else:
   print("Training data could not be loaded or the file was empty.")