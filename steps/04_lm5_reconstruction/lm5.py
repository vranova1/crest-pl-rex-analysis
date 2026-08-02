import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
import os

from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import cross_val_score, KFold
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GroupKFold

import statsmodels.api as sm
from statsmodels.formula.api import ols
from patsy import dmatrices  # Essential for converting formulas to matrices
from sklearn.model_selection import LeaveOneGroupOut
logo = LeaveOneGroupOut()

BASE_PATH = "/home/annav/iocb/Crest-on-PL-REX-dataset"
TABLES_DIR = os.path.join(BASE_PATH, "tables")


traindf = pd.read_csv(os.path.join(TABLES_DIR, 'lm5_features.csv'))
# 2. List the columns used in your model
cols_to_check = ['ConfEntropy', 'NumRotors', 'NumMethyl', 'Ring', 'SG', 'HBond', 'PiStack', 'Target', 'Ligand']

# 3. Drop rows where ANY of these columns are empty
# This ensures X, y, and groups will all have the same length (111)
traindf = traindf.dropna(subset=cols_to_check).reset_index(drop=True)

print(f"Cleaned data: {len(traindf)} samples remaining.")


# --- 1. Original Statsmodels OLS (For the Summary Table) ---
formula = 'ConfEntropy ~ np.log1p(NumRotors) + np.log1p(NumMethyl) + np.log1p(Ring) + np.log1p(SG) + np.log1p(HBond) + np.log1p(PiStack)'
lm5 = ols(formula, traindf).fit()

print(lm5.summary())

# --- 2. Cross-Validation Section ---
# We use dmatrices to ensure the log-transforms are applied exactly as in the formula
y, X = dmatrices(formula, traindf, return_type='dataframe')

# Initialize a standard Linear Regression for CV
# (Note: OLS in statsmodels and LinearRegression in sklearn are mathematically identical)
cv_model = LinearRegression()

# Define the CV strategy (KFold is better for small datasets like 111 ligands)
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Calculate R-squared scores for each fold
cv_r2_scores = cross_val_score(cv_model, X, y, cv=kf, scoring='r2')
cv_mae_scores = cross_val_score(cv_model, X, y, cv=kf, scoring='neg_mean_absolute_error')

print("\n" + "="*30)
print("CROSS-VALIDATION RESULTS (5-Fold)")
print("="*30)
print(f"Individual R2 scores: {cv_r2_scores}")
print(f"Mean R2: {cv_r2_scores.mean():.3f} (+/- {cv_r2_scores.std()*2:.3f})")
print(f"Mean MAE: {abs(cv_mae_scores.mean()):.3f}")
print("="*30 + "\n")

print("----------------- KFold by series ------------------------")
# 1. Define your groups (change 'Series' to whatever your column name is)
groups = traindf['Target'] 

# 2. Setup the GroupKFold
gkf = GroupKFold(n_splits=len(groups.unique())) # Leave-One-Series-Out

# 3. Run the CV
cv_model = LinearRegression()
y, X = dmatrices(formula, traindf, return_type='dataframe')

# We pass the 'groups' array so sklearn knows who belongs together
group_r2_scores = cross_val_score(cv_model, X, y, cv=gkf, groups=groups, scoring='r2')

print(f"Group-wise Mean R2: {group_r2_scores.mean():.3f}")


print(f"{'Target Group':<20} | {'R2 Score':<10}")
print("-" * 35)

scores = []
for train_idx, test_idx in logo.split(X, y, groups=groups):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    
    cv_model.fit(X_train, y_train)
    score = cv_model.score(X_test, y_test)
    
    target_name = groups.iloc[test_idx].iloc[0]
    print(f"{target_name:<20} | {score:>10.3f}")
    scores.append(score)

print("-" * 35)
print(f"Mean Group R2: {np.mean(scores):.3f}")

weights = cv_model.coef_
print(f"Weights (Coefficients): {weights}")

# Retrieve intercept (b)
bias = cv_model.intercept_
print(f"Intercept (Bias): {bias}")

# --- 3. Plotting ---
# Residue Plot and Q-Q Plot
plt.scatter(lm5.fittedvalues, lm5.resid_pearson, s=10) # Made dots bigger for visibility
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel("Fitted Values", size=15)
plt.ylabel("Standardized Residue", size=15)
plt.title("Residual Plot")
plt.show()

sm.qqplot(lm5.resid_pearson, line="s")
plt.xlabel("Theoretical Quantiles", size=15)
plt.ylabel("Sample Quantiles", size=15)
plt.title("Q-Q Plot")
plt.show()