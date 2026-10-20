from pathlib import Path
import json, pandas as pd, joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.neighbors import NearestNeighbors
BASE=Path(__file__).resolve().parent
DATA=BASE / "data" / "meal_planner_foods_all_records.csv"
MODEL_DIR=BASE / "models"; MODEL_DIR.mkdir(exist_ok=True)
df=pd.read_csv(DATA)
numeric=["calories_kcal_per_serving_estimated","protein_g_per_serving_estimated","carbs_g_per_serving_estimated","fat_g_per_serving_estimated","fiber_g_per_serving_estimated","serving_size_g_estimated"]
categorical=["primary_meal_type","cuisine","food_category"]
pre=ColumnTransformer([("num",Pipeline([("imputer",SimpleImputer(strategy="median")),("scale",StandardScaler())]),numeric),("cat",Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]),categorical)])
X=pre.fit_transform(df[numeric+categorical])
knn=NearestNeighbors(n_neighbors=min(16,len(df)),metric="cosine",algorithm="brute").fit(X)
joblib.dump({"preprocessor":pre,"model":knn,"numeric_features":numeric,"categorical_features":categorical,"dataset_path":"data/meal_planner_foods_all_records.csv","model_type":"content_similarity_knn","not_supervised":True},MODEL_DIR/"meal_knn_all_records.joblib")
report={"records":len(df),"unique_food_names":int(df.food_name.str.lower().str.strip().nunique()),"model":"NearestNeighbors cosine similarity over standardized serving nutrition and one-hot meal/cuisine/category features","supervised_labels_used":False,"interpretation":"Similarity retrieval model, not a model trained to predict user likes. Values are approximate and unverified.","features":numeric+categorical}
(MODEL_DIR/"training_report.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
