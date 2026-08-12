import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("sales_data.csv")

print("Total Sales:", df["Sales"].sum())

top_products = df.groupby("Product")["Sales"].sum()
print(top_products.sort_values(ascending=False))

monthly_sales = df.groupby("Month")["Sales"].sum()

monthly_sales.plot(kind="bar")
plt.title("Monthly Sales")
plt.xlabel("Month")
plt.ylabel("Sales")
plt.show()