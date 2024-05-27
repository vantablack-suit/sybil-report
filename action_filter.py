import pandas as pd

# Load the Excel file
file_path = 'C:/Users/.../full_data.xlsx'
full_data_df = pd.read_excel(file_path, sheet_name='full_data')
action_filter_df = pd.read_excel(file_path, sheet_name='action_filter')

# Print column names to verify
print("full_data columns:", full_data_df.columns)
print("action_filter columns:", action_filter_df.columns)

# Ensure correct column names are used
action_column_name = 'Actions'
interaction_column_name = 'Software Interactions'
wallet_column_name = 'Wallet'
filter_action_column_name = 'Action'

# Convert action_filter_df to a dictionary for easy lookup
action_filter_dict = dict(zip(action_filter_df[filter_action_column_name], action_filter_df[interaction_column_name]))

# Initialize an empty set to store matching wallets
matching_wallets = set()

# Convert 'Actions' column to string and fill NaN values with an empty string
full_data_df[action_column_name] = full_data_df[action_column_name].astype(str).fillna('')

# Iterate through each row in full_data_df
for index, row in full_data_df.iterrows():
    wallet = row[wallet_column_name]
    software_interactions = row[interaction_column_name]
    actions = row[action_column_name].split(', ')

    # Check each action in the row
    for action in actions:
        if action in action_filter_dict:
            benchmark = action_filter_dict[action]
            if software_interactions >= benchmark:
                matching_wallets.add(wallet)
                break

# Convert the set to a list for output
matching_wallets_list = list(matching_wallets)

# Convert the list to a DataFrame for display
matching_wallets_df = pd.DataFrame(matching_wallets_list, columns=['Wallet'])

# Save the DataFrame to a CSV file
output_file_path = 'C:/Users/.../matching_wallets.csv'
matching_wallets_df.to_csv(output_file_path, index=False)

# Print the DataFrame to the console
print(matching_wallets_df)
