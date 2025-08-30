import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
import joblib

# Load the dataset
def load_dataset(file_path):
    df = pd.read_csv(file_path)
    return df

# Validate and clean the dataset
def validate_dataset(df):
    # Ensure donation_amount and total_donations are rounded to 2 decimal places
    df['donation_amount'] = df['donation_amount'].round(2)
    df['total_donations'] = df['total_donations'].round(2)

    # Remove rows where donation_amount > total_donations
    df = df[df['donation_amount'] <= df['total_donations']]
    return df

# Preprocess the dataset
def preprocess_data(df):
    # Separate features and target
    X = df.drop(columns=['viewer_id', 'creator_id', 'video_id', 'target'])
    y = df['target']

    # Normalize numerical features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y

# Train the model
def train_model(X_train, y_train):
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train, y_train)
    return model

# Evaluate the model
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred)
    print("Model Evaluation Report:\n", report)

# Save the model
def save_model(model, file_path):
    joblib.dump(model, file_path)
    print(f"Model saved to {file_path}")

# Main function
def main():
    file_path = "data/synthetic_fraud_dataset.csv"

    # Load dataset
    df = load_dataset(file_path)

    # Validate dataset
    df = validate_dataset(df)

    # Preprocess data
    X, y = preprocess_data(df)

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model = train_model(X_train, y_train)

    # Save the model
    save_model(model, "models/fraud_detection_model.pkl")

    # Evaluate the model
    evaluate_model(model, X_test, y_test)

if __name__ == "__main__":
    main()
