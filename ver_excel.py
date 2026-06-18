import pandas as pd

df = pd.read_excel(
    "Polla mundialista.xlsx",
    header=1
)

print(df.columns.tolist())
print(df.head())