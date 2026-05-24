import pandas as pd
import numpy as np

# 1. Load your cleaned product catalog
# Make sure your file is named 'cleaned_catalog.csv' and has 'product id' and 'sales volume'
catalog_df = pd.read_csv('./cleaned_catalog.csv')

# 2. Setup the Date Range (Last 90 Days)
end_date = pd.to_datetime('today')
dates = pd.date_range(end=end_date, periods=90)

sales_data = []

# 3. Loop through each product and distribute the sales
for index, row in catalog_df.iterrows():
    prod_id = row['Product_ID']
    total_sales = row['Sales_Volume']
    
    # This math trick splits the total sales randomly across 90 days
    daily_proportions = np.random.dirichlet(np.ones(90))
    daily_sales = np.round(daily_proportions * total_sales).astype(int)
    
    # Fix slight rounding errors to ensure the sum exactly matches the total_sales
    difference = int(total_sales - daily_sales.sum())
    daily_sales[0] += difference 
    
    # Add a random "Promotion_Flag" (10% chance a day had a promotion)
    promos = np.random.choice([0, 1], size=90, p=[0.9, 0.1])
    
    # 4. Append each day as a new row
    for date, sales, promo in zip(dates, daily_sales, promos):
        # Prevent any negative sales from the rounding fix
        sales = max(0, sales) 
        sales_data.append([date, prod_id, sales, promo])

# 5. Export to CSV
history_df = pd.DataFrame(sales_data, columns=['Date', 'Product_ID', 'Units_Sold', 'Promotion_Flag'])
history_df.to_csv('historical_sales.csv', index=False)

print("Successfully generated historical_sales.csv!")