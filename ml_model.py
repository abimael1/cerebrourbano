from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np
import pandas as pd

class UrbanPredictionModel:
    def __init__(self):
        self.models = {
            'waste': None,
            'traffic': None,
            'air_quality': None,
            'energy': None,
            'public_transport': None,  # New model for public transport
            'public_spaces': None,     # New model for public spaces
            'water': None,             # New model for water consumption
            'urban_growth': None       # New model for urban growth
        }
        self.accuracies = {}
        self.preprocessors = {}

    def prepare_features(self, df, target_type):
        """Prepare features for different prediction types"""
        df = df.copy()
        # Extract temporal features
        df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
        df['month'] = pd.to_datetime(df['date']).dt.month
        df['hour'] = pd.to_datetime(df['date']).dt.hour

        feature_sets = {
            'waste': ['day_of_week', 'month', 'rain', 'is_holiday', 'temperature', 'area'],
            'traffic': ['day_of_week', 'month', 'hour', 'rain', 'is_holiday', 'area'],
            'air_quality': ['temperature', 'humidity', 'wind_speed', 'rain', 'area'],
            'energy': ['temperature', 'hour', 'day_of_week', 'is_holiday', 'area'],
            'public_transport': ['day_of_week', 'hour', 'is_holiday', 'rain', 'area', 'event_nearby'],
            'public_spaces': ['temperature', 'hour', 'day_of_week', 'is_holiday', 'rain', 'area'],
            'water': ['temperature', 'day_of_week', 'month', 'is_holiday', 'area', 'population_density'],
            'urban_growth': ['population_density', 'economic_index', 'infrastructure_score', 'area']
        }

        return df[feature_sets[target_type]]

    def train(self, df, target_type):
        """Train model for specific urban aspect"""
        df = self.prepare_features(df, target_type)
        target_columns = {
            'waste': 'waste_kg',
            'traffic': 'congestion_level',
            'air_quality': 'air_quality_index',
            'energy': 'energy_consumption',
            'public_transport': 'passenger_count',
            'public_spaces': 'occupancy_rate',
            'water': 'water_consumption',
            'urban_growth': 'growth_index'
        }

        X = df.drop(target_columns[target_type], axis=1, errors='ignore')
        y = df[target_columns[target_type]]

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Create preprocessor
        categorical_features = ['area']
        numeric_features = [col for col in X.columns if col not in categorical_features]

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(drop='first', sparse=False), categorical_features)
            ])

        # Create pipeline with appropriate model for each type
        model_dict = {
            'waste': RandomForestRegressor(n_estimators=100),
            'traffic': RandomForestRegressor(n_estimators=100),
            'air_quality': RandomForestRegressor(n_estimators=100),
            'energy': RandomForestRegressor(n_estimators=100),
            'public_transport': RandomForestRegressor(n_estimators=100),
            'public_spaces': RandomForestRegressor(n_estimators=100),
            'water': RandomForestRegressor(n_estimators=100),
            'urban_growth': RandomForestRegressor(n_estimators=100)
        }

        self.models[target_type] = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', model_dict[target_type])
        ])

        # Train the model
        self.models[target_type].fit(X_train, y_train)

        # Calculate accuracy (R² score)
        self.accuracies[target_type] = round(self.models[target_type].score(X_test, y_test) * 100, 2)

        return self.accuracies[target_type]

    def predict(self, features, target_type):
        """Make predictions using the trained model"""
        if self.models[target_type] is None:
            raise ValueError(f"Model for {target_type} needs to be trained first")

        return self.models[target_type].predict(features)

    def get_feature_importance(self, target_type):
        """Get feature importance for the model"""
        if self.models[target_type] is None:
            raise ValueError(f"Model for {target_type} needs to be trained first")

        # Get feature names after preprocessing
        feature_names = (self.models[target_type]
                        .named_steps['preprocessor']
                        .get_feature_names_out())

        # Get importance scores
        importances = self.models[target_type].named_steps['regressor'].feature_importances_

        return pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)