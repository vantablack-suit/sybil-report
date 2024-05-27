import aiohttp
import asyncio
import csv
import logging
import os
import pandas as pd
import dask.dataframe as dd
from dask.diagnostics import ProgressBar

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the URL and headers
url = 'https://pro-openapi.debank.com/v1/user/history_list'
headers = {
    'accept': 'application/json',
    'AccessKey': '...'
}

# Wallet address to fetch data for
wallet_address = '...'

# Paths to be modified by users
snapshot_file_path = r"C:\Users\...\snapshot.csv"
blacklist_file_path = r"C:\Users\...\blacklist.csv"
folder_path = f'C:/Users/.../Bounty Hunter/{wallet_address}'

# List of chain IDs to fetch data from
chain_ids = [
    "eth", "linea", "manta", "blast", "era", "base", "matic", "op", "arb", "scrl",
    "mobm", "zora", "mode", "zklink", "bsc", "celo", "zeta", "dym", "nova",
    "avax", "mnt", "ftm", "btt"
]

# Parameters for the request
params = {
    'id': wallet_address,
    'page_count': 20  # Maximum count as per API documentation
}

# Create a folder for the wallet address if it doesn't exist
os.makedirs(folder_path, exist_ok=True)


async def fetch_chain_data(session, chain_id, semaphore):
    async with semaphore:
        logging.info(f"Starting data fetch for chain {chain_id}")
        local_data = []
        local_params = params.copy()
        local_params['chain_id'] = chain_id
        local_params.pop('start_time', None)
        fetched_rows = 0
        part = 1

        while True:
            try:
                async with session.get(url, headers=headers, params=local_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        history_list = data.get('history_list', [])

                        if history_list:
                            for item in history_list:
                                item['chain_id'] = chain_id
                            local_data.extend(history_list)
                            fetched_rows += len(history_list)
                            local_params['start_time'] = int(history_list[-1]['time_at'])

                            logging.info(f"Chain: {chain_id} - Fetched rows: {fetched_rows}")

                            if fetched_rows >= part * 10000:
                                await save_data_to_csv(chain_id, local_data, part)
                                part += 1
                                local_data = []
                                await asyncio.sleep(60)  # Wait for 1 minute to avoid connection issues

                            if len(history_list) < local_params['page_count']:
                                break
                        else:
                            break
                    else:
                        logging.error(f"Failed to retrieve data for chain {chain_id}: {response.status}")
                        logging.error(f"Response content: {await response.text()}")
                        break
            except Exception as e:
                logging.error(f"Request exception for chain {chain_id}: {e}")
                await asyncio.sleep(60)  # Wait for 1 minute before retrying
                continue

        if local_data:
            await save_data_to_csv(chain_id, local_data, part, final=True)

        logging.info(f"Total rows processed for chain {chain_id}: {fetched_rows}")


async def save_data_to_csv(chain_id, data, part, final=False):
    # Define the output file path
    suffix = '_fin' if final else f'_{part}'
    output_file_path = os.path.join(folder_path, f'{chain_id}{suffix}.csv')
    if data:
        with open(output_file_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            # Write the header based on the keys of the first transaction
            header = data[0].keys()
            csvwriter.writerow(header)
            # Write each transaction as a row
            for item in data:
                csvwriter.writerow(item.values())
        logging.info(f"Transaction data for chain {chain_id} saved to {output_file_path}")


def get_processed_chains():
    processed_chains = set()
    for chain_id in chain_ids:
        output_file_path = os.path.join(folder_path, f'{chain_id}_fin.csv')
        if os.path.exists(output_file_path):
            processed_chains.add(chain_id)
    return processed_chains


async def main():
    async with aiohttp.ClientSession() as session:
        processed_chains = get_processed_chains()
        unprocessed_chain_ids = [chain_id for chain_id in chain_ids if chain_id not in processed_chains]

        # Limit the number of concurrent tasks to 5
        semaphore = asyncio.Semaphore(5)

        tasks = [fetch_chain_data(session, chain_id, semaphore) for chain_id in unprocessed_chain_ids]
        await asyncio.gather(*tasks)

    merge_and_process_csv_files(folder_path, wallet_address)


def merge_and_process_csv_files(folder_path, wallet_address):
    csv_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
    merged_data = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)

    if 'tx' in merged_data.columns:
        merged_data['tx'] = merged_data['tx'].apply(lambda x: eval(x) if isinstance(x, str) else {})
        merged_data['from_addr'] = merged_data['tx'].apply(lambda x: x.get('from_addr', ''))
        merged_data['action'] = merged_data['tx'].apply(lambda x: x.get('name', ''))
        merged_data['from_addr'] = merged_data['from_addr'].astype(str)
        merged_data['action'] = merged_data['action'].astype(str)
        cols = list(merged_data.columns)
        chain_id_index = cols.index('chain_id')
        # Swap columns 2 and 3
        cols[chain_id_index + 1], cols[chain_id_index + 2] = cols[chain_id_index + 2], cols[chain_id_index + 1]
        merged_data = merged_data[cols]

    # Add new first column 'Source'
    merged_data.insert(0, 'Source', wallet_address)

    merged_file_path = os.path.join(folder_path, f'{wallet_address}.csv')
    merged_data.to_csv(merged_file_path, index=False)
    logging.info(f"All data merged and processed into {merged_file_path}")

    for file in csv_files:
        os.remove(file)
        logging.info(f"Removed file {file}")

    wallet_file_path = os.path.join(folder_path, 'wallets.csv')
    unique_wallets = merged_data[['from_addr']].drop_duplicates().reset_index(drop=True)
    unique_wallets.to_csv(wallet_file_path, index=False)
    logging.info(f"Created 'wallets' CSV with unique wallets in {wallet_file_path}")

    df_wallets = pd.read_csv(wallet_file_path)

    # Ensure 'action' column exists and is properly initialized
    if 'action' not in df_wallets.columns:
        df_wallets['action'] = ''

    df_wallets.to_csv(wallet_file_path, index=False)
    logging.info(f"Added 'action' column in {wallet_file_path}")

    source_df = pd.read_csv(merged_file_path)
    source_df['action'] = source_df['action'].astype(str)
    source_actions = source_df.groupby('from_addr')['action'].apply(lambda x: ', '.join(sorted(set(x)))).reset_index()
    merged_df = pd.merge(df_wallets, source_actions, left_on='from_addr', right_on='from_addr', how='left', suffixes=('', '_source'))

    def combine_actions(row):
        actions = set(filter(lambda x: x and x != 'nan', [str(row['action']), str(row['action_source'])]))
        return ', '.join(sorted(actions))

    merged_df['action'] = merged_df.apply(combine_actions, axis=1)
    merged_df.drop(columns=['action_source'], inplace=True)
    merged_df.to_csv(wallet_file_path, index=False)
    logging.info(f"Updated wallets CSV with combined actions in {wallet_file_path}")

    blacklist_df = pd.read_csv(blacklist_file_path)
    filtered_wallets_df = merged_df[~merged_df['from_addr'].isin(blacklist_df['wallet'])]
    filtered_wallets_df.to_csv(wallet_file_path, index=False)
    logging.info(f"Removed blacklisted addresses from {wallet_file_path}")

    snapshot_df = dd.read_csv(snapshot_file_path)

    logging.info("Adding 'Transactions' column to snapshot file")
    with ProgressBar():
        transactions = snapshot_df['SENDER_WALLET'].value_counts().compute()

    logging.info("Adding 'Transactions' column to wallets file")
    df_wallets = pd.read_csv(wallet_file_path)
    transactions = transactions.to_frame(name='Transactions')
    df_wallets = df_wallets.merge(transactions, left_on='from_addr', right_index=True, how='left').fillna(0)
    df_wallets = df_wallets[df_wallets['Transactions'] > 0]
    df_wallets.to_csv(wallet_file_path, index=False)
    logging.info(f"Updated wallets file saved to {wallet_file_path}")


if __name__ == '__main__':
    asyncio.run(main())
