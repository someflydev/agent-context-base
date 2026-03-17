# Python ML and Data Science Library Selection

This is the first place to look when a Python repo needs data processing, ML training, or inference capability. The answer here is opinionated — use the right library for the specific task, not the most familiar one.

## Quick Decision Table

| Task | Primary library | Notes |
|---|---|---|
| Tabular data processing, transforms, filtering | **Polars** | Default. Not pandas. |
| Supervised learning: classification, regression | **scikit-learn** | Pipelines, cross-val, metrics |
| Gradient-boosted trees on tabular data | **XGBoost or LightGBM** | Outperform sklearn trees on most tabular tasks |
| Array math, vectorized numerical ops | **NumPy** | Required by sklearn; also use for custom loss functions and low-level ops |
| Statistical tests, optimization, sparse matrices | **SciPy** | ANOVA, t-tests, least-squares, curve fitting |
| Time series statistical inference (ARIMA, OLS) | **statsmodels** | When p-values and confidence intervals are required |
| Text embeddings, semantic search | **sentence-transformers** | Hugging Face wrapper; GPU optional |
| General NLP, LLM fine-tuning, transformer models | **transformers (Hugging Face)** | For custom model classes; sentence-transformers handles the embedding use case with less boilerplate |
| Clustering, dimensionality reduction | **scikit-learn** | KMeans, DBSCAN, PCA, UMAP (via umap-learn) |
| Polars-to-sklearn bridge | **narwhals or .to_numpy() / .to_pandas()** | See below |
| Data loading and schema validation | **Polars + Pydantic** | Not pandas; not csv.reader |


## Polars vs pandas: Why Polars Is the Default

1. **No index.** pandas attaches a mutable row index to every DataFrame. This index is a source of silent bugs: misaligned indices after joins or concatenations produce NaN rows that are easy to miss. Polars has no row index — rows are positional only, which eliminates an entire class of alignment bugs.

2. **Lazy evaluation.** `pl.scan_parquet()`, `pl.scan_csv()`, and `.lazy()` on an existing DataFrame defer computation until `.collect()` is called. The lazy graph is optimized before execution: projection pruning (only touched columns are read from disk), predicate pushdown (filters applied as early as possible), and query plan simplification. In pandas, every operation materializes immediately — there is no query optimizer.

3. **Expression API.** Polars expressions (`pl.col("x").cast(pl.Float64).log()`) are composable, parallelizable, and executed in Rust. The pandas equivalent (`df["x"].apply(...)`) is Python-loop speed and single-threaded.

4. **Memory efficiency.** Polars uses Apache Arrow memory layout natively. Columns are contiguous in memory; operations that touch one column do not load others. pandas stores each column as a separate numpy array but with metadata overhead per-series. For wide DataFrames (hundreds of columns), Polars' memory footprint is substantially smaller.

5. **Null semantics.** Polars uses Arrow null bitmask (explicit null per value) for all types. pandas uses NaN (float sentinel) for nulls in integer and bool columns, which coerces column types and produces silent casting on operations. A pandas "int column" with a null becomes a float column — Polars maintains the declared type.

6. **String operations.** Polars string operations (`pl.col("x").str.starts_with("acme")`) run in parallel over all cores. pandas string operations are Python-speed loops.

When pandas is still needed:
- **Library interop**: some sklearn estimators, matplotlib/seaborn plotting functions, and certain data source adapters accept only pandas DataFrames. Convert at the boundary: `df.to_pandas()` (Polars → pandas) or `pl.from_pandas(df)` (pandas → Polars). Keep the conversion at the library boundary — do not use pandas for the processing pipeline.
- **Legacy repos**: existing repos that depend heavily on pandas conventions should not be migrated wholesale. Add Polars for new code paths; use `pl.from_pandas()` to bridge.
- **pandas-only ecosystems**: xarray (multi-dimensional data), geopandas (geospatial), and some time-series libraries are pandas-native. These are specialized; for general tabular ML, Polars is correct.


## scikit-learn: When To Reach For It

Reach for scikit-learn when:
- **Supervised learning**: the task is classification (`LogisticRegression`, `RandomForest`, `SVM`, `GradientBoostingClassifier`), regression (`LinearRegression`, `Ridge`, `ElasticNet`), or structured prediction.
- **sklearn Pipeline**: the task involves chaining feature preprocessing steps with a model in a cross-validated, reproducible way. Use `sklearn.pipeline.Pipeline` to chain `ColumnTransformer`, `StandardScaler`, `OneHotEncoder`, and estimators.
- **Model evaluation**: `cross_val_score`, `GridSearchCV`, `RandomizedSearchCV`, `train_test_split` are the canonical evaluation tools. Do not implement cross-validation manually.
- **Feature engineering**: `StandardScaler`, `MinMaxScaler`, `OneHotEncoder`, `OrdinalEncoder`, `PolynomialFeatures`, `TruncatedSVD` are the right tools. Do NOT do feature scaling by hand when sklearn's preprocessors handle it correctly — fit on train, transform both train and test separately.
- **Clustering**: `KMeans`, `DBSCAN`, `AgglomerativeClustering` when the number of clusters is unknown or the task is exploratory.
- **Dimensionality reduction**: `PCA`, `TruncatedSVD` (sparse matrices), `UMAP` (via umap-learn).
- **Metrics**: `sklearn.metrics` has `classification_report`, `confusion_matrix`, `roc_auc_score`, `mean_squared_error`, and more. Do not implement these from scratch.

Do NOT use scikit-learn when:
- **Data processing and transforms**: cleaning columns, filtering rows, joining tables, computing rolling aggregations — these belong in Polars, not sklearn preprocessing. sklearn's `ColumnTransformer` is for model-adjacent feature scaling/encoding, not ETL. Do not use sklearn `ColumnTransformer` for ETL steps.
- **Gradient-boosted trees on tabular data**: XGBoost and LightGBM consistently outperform sklearn's `GradientBoostingClassifier` on structured tabular data and run faster (multi-threaded). Use them instead.
- **NLP or embeddings**: use sentence-transformers for embedding tasks, transformers for fine-tuning LLMs. sklearn's text tools (`TfidfVectorizer`) are for classical NLP (bag of words), not modern semantic embedding.
- **Large datasets that don't fit in memory**: sklearn is in-memory only. Use Polars lazy evaluation for large-scale processing; use Dask-ML or specialized tools for truly out-of-core learning.

Polars-to-sklearn bridge:

sklearn estimators accept NumPy arrays or pandas DataFrames. Convert at the model boundary:

```python
X_train = df.select(["feature_a", "feature_b"]).to_numpy()
y_train = df["label"].to_numpy()
```

Never convert the whole DataFrame to pandas for sklearn — convert only the columns needed.


## NumPy: When To Reach For It

NumPy is the foundational array library. Most of the time it enters the codebase through sklearn or scipy rather than directly. Reach for it directly when:

- **Custom loss functions or scoring metrics**: when sklearn's built-in metrics don't cover the task and you need vectorized array math.
- **Low-level numerical operations**: matrix multiplication, eigendecomposition (`np.linalg`), Fourier transforms (`np.fft`), sorting, binning, histogramming.
- **Seeding and reproducibility**: `np.random.default_rng(seed)` for reproducible random splits or data augmentation.
- **Interfacing with C extensions**: functions that accept buffer pointers expect NumPy arrays.

Do NOT use NumPy when:
- The operation is a tabular data transform — use Polars.
- The operation is a statistical test — use SciPy.
- The operation is an ML training step — use sklearn, XGBoost, or LightGBM.

NumPy is for raw array math. If a higher-level library already wraps the operation, use it.


## SciPy: When To Reach For It

Reach for scipy when:
- **Statistical tests**: `scipy.stats.ttest_ind` (independent t-test), `mannwhitneyu` (non-parametric), `chi2_contingency` (chi-squared), `f_oneway` (one-way ANOVA), `ks_2samp` (Kolmogorov-Smirnov). Use these when you need a p-value, not just a metric.
- **Curve fitting and optimization**: `scipy.optimize.curve_fit`, `minimize` (gradient-free and gradient-based optimization), `linprog` (linear programming).
- **Sparse matrices**: `scipy.sparse` for high-dimensional sparse data (e.g., TF-IDF matrices with 100k+ features). sklearn's `TruncatedSVD`, `NaiveBayes`, and `SVM` accept scipy sparse matrices directly.
- **Signal processing**: `scipy.signal` for filtering, spectral analysis, convolution (uncommon in general ML pipelines, but the right tool when needed).
- **Distance matrices**: `scipy.spatial.distance` for pairwise distance computation.

Do NOT use scipy when:
- The task is supervised ML — use sklearn.
- The task is tabular data processing — use Polars.
- The task is gradient-boosted trees — use XGBoost or LightGBM.


## XGBoost and LightGBM: When To Use Over sklearn

Reach for XGBoost (`xgboost`) or LightGBM (`lightgbm`) instead of sklearn's gradient boosting when:
- The task is tabular classification or regression and you want state-of-the-art performance. Both consistently outperform sklearn's `GradientBoostingClassifier` on structured tabular data.
- Training data has more than ~50k rows — XGBoost and LightGBM use histogram-based splitting (LightGBM) or exact greedy with approximate fallback (XGBoost) that is 10–100x faster than sklearn's `GradientBoostingClassifier`.
- Categorical features are present: LightGBM has native categorical support (`feature_name` + `categorical_feature` parameter) without one-hot encoding.
- GPU training is available: both support CUDA acceleration (`device="cuda"` in XGBoost, `device="gpu"` in LightGBM).

Both implement the sklearn estimator interface (`fit`/`predict`/`predict_proba`), so they drop into sklearn `Pipeline`s and `GridSearchCV` without changes.

Choose XGBoost when: the model will be deployed in a polyglot environment (XGBoost models export to C++ and ONNX); or when the codebase already uses XGBoost.

Choose LightGBM when: training speed matters most; or when categorical features are present and you want to avoid one-hot encoding.


## statsmodels: When To Reach For It

Reach for statsmodels when:
- **OLS with inference**: you need coefficient p-values, confidence intervals, R², and F-statistics — not just predictions. `statsmodels.api.OLS` gives a full summary table. sklearn's `LinearRegression` gives only predictions.
- **ARIMA / SARIMA**: time series forecasting with AutoRegressive Integrated Moving Average models. `statsmodels.tsa.arima.model.ARIMA` is the standard. Use this when the task is statistical forecasting, not deep learning time series.
- **Logit/Probit regression with inference**: when the task is binary classification AND you need coefficient significance (e.g., explaining which features are statistically significant predictors).
- **Panel data models**: fixed effects, random effects (`statsmodels.stats.sandwich_covariance`).

Do NOT use statsmodels when:
- You only need predictions (not inference) — use sklearn or XGBoost.
- The time series is long and nonlinear — use a gradient-boosted tree or LSTM.
- You don't need p-values or confidence intervals.


## sentence-transformers and transformers: When To Reach For Them

**sentence-transformers:**

Reach for this when:
- The task is semantic similarity, text embedding, or semantic search.
- Embeddings will be stored in a vector store (Qdrant, pgvector, Meilisearch).
- You need a sentence embedding in <5 lines of code without managing transformer internals.

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(["sentence one", "sentence two"])
```

**transformers (Hugging Face):**

Reach for this when:
- Fine-tuning a transformer model on a custom dataset.
- Loading a model with a custom classification head.
- Running generation (GPT-style text generation, summarization, translation).
- The task requires direct access to the tokenizer, model weights, or attention outputs.

Do NOT add transformers to a service that only needs embeddings — sentence-transformers wraps transformers and provides a simpler interface for the embedding use case. Adding the full transformers library directly introduces unnecessary complexity.


## The Data Pipeline vs Model Pipeline Distinction

This is the most common architectural mistake in Python ML repos. Treat these as separate layers with a clean boundary:

```python
# Data pipeline (Polars)
df = (
    pl.scan_parquet("data/*.parquet")
    .filter(pl.col("label").is_not_null())
    .with_columns([
        pl.col("amount").log1p().alias("log_amount"),
        pl.col("category").cast(pl.Utf8),
    ])
    .collect()
)

# Model boundary (numpy conversion)
feature_cols = ["log_amount", "days_since", "score"]
X = df.select(feature_cols).to_numpy()
y = df["label"].to_numpy()

# Model pipeline (sklearn / XGBoost / LightGBM)
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", XGBClassifier(n_estimators=300, device="cpu")),
])
pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)

# Post-model (Polars)
results_df = pl.DataFrame({"id": ids, "prediction": y_pred})
results_df.write_parquet("predictions/output.parquet")
```

Common mistakes:
- Doing ETL transforms inside sklearn `ColumnTransformer` (use Polars for ETL, sklearn for model-adjacent feature scaling only).
- Converting the whole DataFrame to pandas before passing to sklearn (convert only the feature columns as numpy arrays at the model boundary).
- Using pandas throughout the data pipeline because sklearn "requires" it (sklearn accepts numpy arrays; only a few older estimators required a pandas index).


## Common Assistant Mistakes

- Adding pandas as a dependency when the task is tabular data processing — Polars is the default; pandas only enters at the model boundary if needed.
- Using `sklearn.GradientBoostingClassifier` instead of XGBoost or LightGBM on tabular data.
- Implementing custom metric calculation instead of using `sklearn.metrics`.
- Using statsmodels for a prediction task instead of sklearn (use statsmodels only when inference and p-values are required).
- Adding the full transformers library for an embedding task that sentence-transformers handles in five lines.
- Doing feature scaling manually (dividing by std, subtracting mean) instead of using `sklearn.preprocessing.StandardScaler` inside a Pipeline.
- Converting a Polars DataFrame to pandas for the entire pipeline instead of converting only the feature columns to numpy at the model boundary.
- Using sklearn `Pipeline` for ETL steps (filtering rows, joining tables, string cleaning) — sklearn Pipelines are for model-adjacent feature engineering and estimators, not ETL.


## Related

- context/stacks/python-fastapi-uv-ruff-orjson-polars.md
- context/stacks/duckdb-parquet.md (if loading this doc, data is probably Parquet-native)
- context/stacks/duckdb-trino-polars.md (for analytical pipelines that also query DuckDB)
- context/stacks/qdrant.md (if embeddings go to a vector store)
