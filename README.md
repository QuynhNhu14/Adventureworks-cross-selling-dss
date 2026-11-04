# AdventureWorks Cross-Selling Decision Support System

A Streamlit-based decision support system that recommends complementary products using association rules mined with the FP-Growth algorithm from the AdventureWorks transaction dataset.

## Project Objectives

This project is designed to support cross-selling decisions by helping users:

- Recommend products that are frequently purchased together.
- Analyze association rules using Support, Confidence, and Lift.
- Identify product pairs that may be suitable for bundles.
- Support product placement and cross-promotion decisions.
- Highlight products that may require coordinated inventory monitoring.
- Improve average order value and sales revenue through relevant product recommendations.

## Project Architecture

```text
AdventureWorks Transaction Data
            ↓
5-Dimension Data Warehouse
            ↓
Incremental ETL and Data Validation
            ↓
Feature Store / Basket Data
            ↓
FP-Growth Frequent Pattern Mining
            ↓
Association Rules
            ↓
Streamlit Cross-Selling DSS
```

## Data Warehouse Model

The final data warehouse follows a star schema with one fact table and five dimensions:

- `DimDate`
- `DimCustomer`
- `DimProduct`
- `DimPromotion`
- `DimSalesTerritory`
- `FactSales`

The grain of `FactSales` is one row per sales order detail line, identified by:

```text
SalesOrderID + SalesOrderDetailID
```

## FP-Growth Model Results

The final FP-Growth run produced the following results:

- Qualified baskets: **21,204**
- Distinct products: **266**
- Basket-item rows: **110,998**
- Frequent itemsets: **844**
- Association rules: **1,098**
- Model version: `FPG_20261104_011732`
- Market Basket Run ID: `3`

## FP-Growth Configuration

```python
MIN_SUPPORT = 0.01
MIN_CONFIDENCE = 0.20
MIN_LIFT = 1.20
MAX_LEN = 2
```

`MAX_LEN = 2` is used because the application focuses on one-to-one cross-selling rules:

```text
Product A → Product B
```

This setting does not limit a transaction to two products. Transactions containing multiple products still contribute all eligible two-product combinations.

## Understanding the Metrics

### Support

Support measures how frequently two products appear together across all qualified baskets.

```text
Support(A → B) = Baskets containing A and B / Total baskets
```

### Confidence

Confidence measures how often product B appears in baskets that already contain product A.

```text
Confidence(A → B) = Support(A and B) / Support(A)
```

### Lift

Lift compares the probability of purchasing product B when product A is present with the normal probability of purchasing product B.

```text
Lift(A → B) = Confidence(A → B) / Support(B)
```

Interpretation:

- `Lift > 1`: positive association.
- `Lift = 1`: products are approximately independent.
- `Lift < 1`: negative association.

Association rules describe co-occurrence patterns and do not prove causation.

## Example Recommendation

One of the strongest rules is:

```text
Cable Lock → Minipump
```

Approximate metrics:

- Support: **1.14%**
- Confidence: **93.41%**
- Lift: **74.18**

This means that approximately 93.41% of qualified baskets containing a Cable Lock also contain a Minipump. However, the pair appears in approximately 1.14% of all qualified baskets, so the rule should be treated as a strong association within a specific transaction segment rather than the most common pair across the entire dataset.

## Application Features

The Streamlit application provides:

- A product selector for the item currently viewed or selected by a customer.
- Top-N complementary-product recommendations.
- Minimum Support, Confidence, and Lift filters.
- Association-rule KPI cards.
- A recommendation table with business-action suggestions.
- A bar chart for top complementary products.
- A Support-versus-Confidence scatter plot sized by Lift.
- A complete filtered association-rule table.

## Business Action Classification

The application assigns a suggested business action to each rule.

### Bundle and Coordinated Inventory Priority

Applied when:

```text
Support >= 2%
Confidence >= 50%
Lift >= 2
```

Possible actions:

- Create a product bundle.
- Display the products together.
- Coordinate inventory monitoring.
- Test a cross-promotion campaign.

### Targeted Cross-Sell

Applied when:

```text
Confidence >= 50%
Lift >= 2
```

Possible actions:

- Recommend the consequent product when the antecedent product is selected.
- Use contextual recommendations instead of a broad promotion.
- Test the recommendation with a specific customer or transaction segment.

### Monitor or Test a Small Promotion

Applied when:

```text
Lift >= 1.20
```

Possible actions:

- Monitor the product pair.
- Run a small promotional experiment.
- Collect more evidence before a larger campaign.

These classifications are demonstration business rules. They are not automatically learned by FP-Growth.

## Repository Structure

```text
.
├── app.py
├── association_rules_FPG_20261104_011732.csv
├── requirements.txt
├── README.md
└── .gitignore
```

## Technology Stack

- Python 3.12
- Streamlit
- pandas
- Plotly
- FP-Growth
- mlxtend
- Microsoft SQL Server 2022
- Docker
- AdventureWorks

## Local Installation

### 1. Clone the Repository

```bash
git clone https://github.com/quynhnhu14/adventureworks-cross-selling-dss.git
cd adventureworks-cross-selling-dss
```

### 2. Create a Virtual Environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Run the Application

```bash
python -m streamlit run app.py
```

Open the application at:

```text
http://localhost:8501
```

### 5. Stop the Application

Press:

```text
Ctrl+C
```

in the terminal running Streamlit.

## Requirements

The `requirements.txt` file should contain:

```text
streamlit>=1.40
pandas>=2.0
plotly>=5.20
```

## Expected Validation Results

After starting the application, verify the following:

- Total rules: **1,098**
- Average Confidence: approximately **53.40%**
- Average Lift: approximately **18.02**
- Maximum Lift: approximately **74.18**
- Selecting `Cable Lock` returns `Minipump` as a recommendation.

## CSV Input

The application currently reads:

```text
association_rules_FPG_20261104_011732.csv
```

The CSV must be stored in the same directory as `app.py`.

The application uses the CSV snapshot to provide a stable demonstration that does not require SQL Server, Docker, Tailscale, Azure VM, or an on-premises gateway to remain online.

## Optional SQL Server Integration

A future version can replace CSV loading with a query against:

```sql
SELECT *
FROM dbo.vw_LatestAssociationRules;
```

Database credentials must be stored securely using Streamlit secrets or environment variables. Do not commit passwords, tokens, `.env` files, or `.streamlit/secrets.toml` to GitHub.

## Deployment to Streamlit Community Cloud

1. Push the repository to GitHub.
2. Sign in to Streamlit Community Cloud.
3. Select **Create app**.
4. Choose the GitHub repository.
5. Set the main file path to:

```text
app.py
```

6. Select **Deploy**.

Because the current application uses a committed CSV snapshot, no database credentials are required for deployment.

## Limitations

- Association rules identify co-occurrence, not causation.
- High Lift should not be evaluated without Support.
- The current model provides general cross-selling recommendations and is not personalized for individual customers.
- Inventory order quantities cannot be determined from association rules alone.
- Inventory planning also requires stock levels, lead time, supplier information, cost, margin, and seasonality.
- Product-quality improvement decisions require additional data such as reviews, complaints, returns, and warranty claims.

## Future Improvements

Possible extensions include:

- Territory-specific association rules.
- Promotion-specific association rules.
- Time-based market basket analysis.
- Direct SQL Server integration.
- Customer-specific recommendations.
- Inventory and margin-aware ranking.
- A/B testing for bundle and cross-promotion strategies.
- User authentication and role-based access.

## Author

**PHAN THỊ QUỲNH NHƯ**

## License

This project is intended for educational and demonstration purposes.
