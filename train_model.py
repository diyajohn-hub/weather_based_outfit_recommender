import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import pickle

print("Initializing Machine Learning Pipeline...")


df = pd.read_csv('model_training_data.csv')


X = df.drop(columns=['time', 'Outfit_Category'])
y = df['Outfit_Category']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


model = RandomForestClassifier(n_estimators=100, random_state=42)


print("🏋️‍♂️ Training the Random Forest model on historical weather patterns...")
model.fit(X_train, y_train)


y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("\n📊 --- MODEL EVALUATION METRICS ---")
print(f"Overall Accuracy: {accuracy * 100:.2f}%")
print("\nDetailed Performance Report:")
print(classification_report(y_test, y_pred))


with open('outfit_model.pkl', 'wb') as file:
    pickle.dump(model, file)

print("💾 Success! Trained model saved to disk as 'outfit_model.pkl'")