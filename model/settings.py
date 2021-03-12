estimator_params = {
    "SVC": dict(C=0.55, gamma=0.01, degree=4, kernel='rbf'),
    "KNeighborsClassifier": dict(n_neighbors=100, weights='distance'),
    "AdaBoostClassifier": dict(n_estimators=200),
    "GradientBoostingClassifier": dict(max_depth=1, max_features='sqrt'),
    "RandomForestRegressor": dict(n_estimators=200),
    "RandomForestClassifier": dict(n_estimators=200),
    "GradientBoostingRegressor": {
        "n_estimators": 200,
        "max_features": "auto",
        "max_leaf_nodes": None,
    },
    "Ridge": {
        "alpha": 20000,
    },
    "Lasso": {"alpha": 1},
    "LogisticRegression": dict(C = 1e6, max_iter = 100000, multi_class = "ovr")
}

grid_search = False

delete_outliers_bool = True
