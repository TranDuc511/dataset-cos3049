import pandas as pd
import numpy as np

customerpath = r"C:\Users\Admin\Documents\dataset\dataset\customers.json"
transactionpath = r"C:\Users\Admin\Documents\dataset\dataset\transactions.json"

cust = pd.read_json(customerpath)
trans = pd.read_json(transactionpath)

#merge 
df = pd.merge(trans, cust, left_on='Sender Account ID', right_on='Customer ID', how='left')

# Xóa cột thừa và Lưu file
df = df.drop(columns=['Customer ID']) # Delete duplicate ID
df = df.fillna(0) # write 0 in blank spaces

save_path = f'dataset/merged/data.json'
df.to_json (save_path, orient='records', indent=4)
print("Done")
