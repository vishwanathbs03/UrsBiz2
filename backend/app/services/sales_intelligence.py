from __future__ import annotations
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from app.schemas.sales_intelligence import (
    SalesIntelligenceResponse,
    DatasetHealth,
    TopCustomer,
    ProductClassification,
    TopProduct,
    DemandForecastPoint,
    ProductionGap
)

class SalesIntelligenceService:
    # Fuzzy mapping for common column aliases
    COLUMN_ALIASES = {
        "date": ["date", "timestamp", "order_date", "txn_date", "sale_date", "invoice_date"],
        "customer": ["customer", "client", "customer_id", "customer_name", "buyer", "customer code"],
        "product": ["product", "item", "sku", "product_id", "product_name", "item_name", "product code"],
        "quantity": ["qty", "quantity", "units", "units_sold", "volume", "quantity_sold"],
        "price": ["price", "unit_price", "selling_price", "rate"],
        "revenue": ["revenue", "sales", "sales_amount", "amount", "total", "total_amount"]
    }

    def analyze(self, file_content: bytes, filename: str) -> SalesIntelligenceResponse:
        # 1. Load Data
        if filename.endswith('.csv'):
            from io import BytesIO
            df = pd.read_csv(BytesIO(file_content))
        elif filename.endswith(('.xls', '.xlsx')):
            from io import BytesIO
            df = pd.read_excel(BytesIO(file_content))
        else:
            raise ValueError("Unsupported file format")

        # 2. Column Mapping
        mapping = self._map_columns(df.columns)
        df = df.rename(columns={v: k for k, v in mapping.items()})

        # Ensure required columns exist
        required = ["date", "customer", "product", "quantity", "revenue"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        # 3. Cleaning
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')

        initial_rows = len(df)
        df = df.dropna(subset=['date', 'customer', 'product', 'quantity', 'revenue'])
        df = df.drop_duplicates()
        df = df.sort_values('date')
        valid_rows = len(df)

        # 4. Dataset Health
        missing_vals = df[required].isnull().sum().to_dict()
        health_score = (valid_rows / initial_rows * 100) if initial_rows > 0 else 0

        # 5. Customer Patterns
        cust_analysis = self._analyze_customers(df)

        # 6. Product Intelligence
        prod_analysis = self._analyze_products(df)

        # 7. Demand Forecast
        forecast_data, confidence, explanation = self._compute_forecast(df)

        # 8. Production Gap (Simplified MVP: Check if 'inventory' exists in original df)
        # In a real scenario, this might be a separate upload or DB lookup
        prod_gap = None
        if 'inventory' in df.columns:
            inventory_val = pd.to_numeric(df['inventory'], errors='coerce').sum()
            # Use latest baseline forecast as requirement
            req = forecast_data[0].baseline if forecast_data else 0
            gap = req - inventory_val
            prod_gap = ProductionGap(
                required=req,
                available=inventory_val,
                gap=gap,
                status="Shortage" if gap > 0 else "Surplus" if gap < 0 else "Balanced"
            )

        return SalesIntelligenceResponse(
            dataset_health=DatasetHealth(
                total_rows=initial_rows,
                valid_rows=valid_rows,
                missing_values=missing_vals,
                health_score=health_score
            ),
            customer_patterns=cust_analysis['segments'],
            top_customers=cust_analysis['top'],
            product_intelligence=prod_analysis['classifications'],
            top_products=prod_analysis['top'],
            demand_forecast=forecast_data,
            production_gap=prod_gap,
            forecast_confidence=confidence,
            confidence_explanation=explanation
        )

    def _map_columns(self, columns: List[str]) -> Dict[str, str]:
        mapping = {}
        cols_lower = [c.lower() for c in columns]
        for target, aliases in self.COLUMN_ALIASES.items():
            for alias in aliases:
                if alias in cols_lower:
                    # Find original casing
                    idx = cols_lower.index(alias)
                    mapping[target] = columns[idx]
                    break
        return mapping

    def _analyze_customers(self, df: pd.DataFrame) -> Dict:
        cust_df = df.groupby('customer').agg({
            'date': [lambda x: (x.max() - x.min()).days, 'count'],
            'revenue': 'sum'
        })
        cust_df.columns = ['lifespan', 'order_count', 'total_revenue']

        # Segments
        new = len(cust_df[cust_df['order_count'] == 1])
        repeat = len(cust_df[cust_df['order_count'] > 1])

        # High Value: Top 20%
        revenue_threshold = cust_df['total_revenue'].quantile(0.8)
        high_value = len(cust_df[cust_df['total_revenue'] >= revenue_threshold])

        # At Risk: No orders in last 30% of time range
        total_range = (df['date'].max() - df['date'].min()).days
        risk_window = total_range * 0.3
        last_purchase = df.groupby('customer')['date'].max()
        at_risk = len(last_purchase[last_purchase < (df['date'].max() - timedelta(days=risk_window))])

        top = [
            TopCustomer(name=name, revenue=row['total_revenue'], rank=i+1)
            for i, (name, row) in enumerate(cust_df.sort_values('total_revenue', ascending=False).head(5).iterrows())
        ]

        return {
            'segments': {'new': new, 'repeat': repeat, 'high_value': high_value, 'at_risk': at_risk},
            'top': top
        }

    def _analyze_products(self, df: pd.DataFrame) -> Dict:
        # Volume by product
        prod_vol = df.groupby('product')['quantity'].sum().sort_values(ascending=False)
        top_prod = [
            TopProduct(product=name, revenue=df[df['product']==name]['revenue'].sum(), volume=vol)
            for name, vol in prod_vol.head(5).items()
        ]

        # Classifications (Growing/Declining)
        # Split data into last 3 months and previous 3 months
        last_date = df['date'].max()
        cutoff_recent = last_date - timedelta(days=90)
        cutoff_prior = last_date - timedelta(days=180)

        recent = df[df['date'] >= cutoff_recent].groupby('product')['quantity'].sum()
        prior = df[(df['date'] >= cutoff_prior) & (df['date'] < cutoff_recent)].groupby('product')['quantity'].sum()

        classifications = []
        for prod in df['product'].unique():
            r_vol = recent.get(prod, 0)
            p_vol = prior.get(prod, 0)

            if p_vol == 0:
                cat = "Stable"
                delta = 0.0
            else:
                delta = (r_vol - p_vol) / p_vol
                if delta > 0.1: cat = "Growing"
                elif delta < -0.1: cat = "Declining"
                else: cat = "Stable"

            # Override if in top 10% volume
            if prod in prod_vol.head(int(len(prod_vol)*0.1)).index:
                cat = "Fast Moving"

            classifications.append(ProductClassification(product=prod, category=cat, volume_delta=delta))

        return {
            'classifications': classifications,
            'top': top_prod
        }

    def _compute_forecast(self, df: pd.DataFrame) -> Tuple[List[DemandForecastPoint], str, str]:
        # Aggregate total quantity by month
        df['month'] = df['date'].dt.to_period('M')
        monthly = df.groupby('month')['quantity'].sum().sort_index()

        if len(monthly) < 3:
            return [], "Low", "Insufficient historical data for reliable forecast (minimum 3 months required)."

        # Weighted Moving Average (WMA)
        # Weights: 0.5, 0.3, 0.2 for last 3 months
        vals = monthly.values[-3:]
        baseline = (vals[-1] * 0.5) + (vals[-2] * 0.3) + (vals[-3] * 0.2)

        # Uncertainty: StdDev of last 6 months
        history = monthly.values[-6:]
        std = np.std(history) if len(history) > 1 else baseline * 0.1

        # Generate 3 months forecast
        forecast = []
        last_month = monthly.index[-1]
        for i in range(1, 4):
            period = (last_month + i).strftime('%Y-%b')
            forecast.append(DemandForecastPoint(
                period=period,
                baseline=max(0, baseline),
                upper_bound=max(0, baseline + std),
                lower_bound=max(0, baseline - std)
            ))

        confidence = "High" if len(monthly) >= 12 else "Medium" if len(monthly) >= 6 else "Low"
        explanation = f"Based on {len(monthly)} months of sales history with a weighted moving average baseline."

        return forecast, confidence, explanation
