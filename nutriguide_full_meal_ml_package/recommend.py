from pathlib import Path
import argparse, pandas as pd, joblib
BASE=Path(__file__).resolve().parent
DATA=BASE/"data"/"meal_planner_foods_all_records.csv"
ART=BASE/"models"/"meal_knn_all_records.joblib"
def recommend(meal="lunch", target_calories=400, count=5, exclude_ids=None):
    df=pd.read_csv(DATA); art=joblib.load(ART); exclude_ids=set(map(str,exclude_ids or []))
    meal=meal.lower(); mask=df.meal_types.fillna("").str.lower().str.split("|").apply(lambda xs: meal in [x.strip() for x in xs])
    pool=df[mask & ~df.food_id.astype(str).isin(exclude_ids) & ~df.is_alcoholic_or_alcohol_based.fillna(False)].copy()
    if pool.empty: return pool
    # Rank by closeness to target calories per serving; similarity model provides tie-break diversity via nearest-neighbour neighborhoods
    pool["calorie_gap"]=abs(pool.calories_kcal_per_serving_estimated-target_calories)
    pool=pool.sort_values(["calorie_gap","food_name"]).head(max(count*5,count))
    feats=art["numeric_features"]+art["categorical_features"]
    X=art["preprocessor"].transform(pool[feats])
    # simple diverse greedy selection in transformed feature space; keep requested number of unique items
    import numpy as np
    chosen=[]; remaining=list(range(len(pool)))
    while remaining and len(chosen)<count:
        if not chosen: idx=remaining[0]
        else:
            # among the top calorie-fit candidates, select the candidate most dissimilar to those chosen
            distances=[]
            for i in remaining:
                sims=[]
                for j in chosen:
                    a=X[i]; b=X[j]
                    dot=float(a.multiply(b).sum()) if hasattr(a,"multiply") else float(np.dot(a,b))
                    na=float(np.sqrt(a.multiply(a).sum())) if hasattr(a,"multiply") else float(np.linalg.norm(a))
                    nb=float(np.sqrt(b.multiply(b).sum())) if hasattr(b,"multiply") else float(np.linalg.norm(b))
                    sims.append(dot/(na*nb) if na and nb else 0.0)
                distances.append((max(sims),i))
            idx=min(distances)[1]
        chosen.append(idx); remaining.remove(idx)
    result=pool.iloc[chosen].copy()
    cols=["food_id","food_name","meal_types","serving_size_g_estimated","calories_kcal_per_serving_estimated","protein_g_per_serving_estimated","carbs_g_per_serving_estimated","fat_g_per_serving_estimated","estimate_confidence","nutrition_estimation_method"]
    return result[cols]
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--meal",default="lunch",choices=["breakfast","lunch","dinner","snacks"]); p.add_argument("--target-calories",type=float,default=400); p.add_argument("--count",type=int,default=5); p.add_argument("--exclude-id",action="append",default=[]); a=p.parse_args()
    print(recommend(a.meal,a.target_calories,a.count,a.exclude_id).to_string(index=False))
