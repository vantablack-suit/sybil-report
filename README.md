# Reported Addresses

reported_addresses.csv

# Description

Report on 52,621 wallets identified as LayerZero Sybil wallets (52,676 unfiltered) after analyzing the code of 5 open-source software programs used for Sybil activities. These programs utilized personal referral addresses of software developers, which were used to trace and identify Sybil users.

**Software 1: zkSync by CZBag**

- Total Wallets Identified: 45,409
- Sybil Wallets Identified: 45,404
- Repository: https://github.com/czbag/zksync
- Referral Address: 0x1c7ff320ae4327784b464eed07714581643b36a7
- Modules and Strings:
	- zksync-main/modules/inch.py - 36
	- zksync-main/modules/openocean.py - 34
	- zksync-main/modules/rocketsam.py - 55
	- zksync-main/modules/xyswap.py - 55
	- zksync-main/modules/zkstars.py - 37

**Software 2: AttackMachine by RealAskaer**

- Total Wallets Identified: 9,415
- Sybil Wallets Identified: 9,393
- Repository: https://github.com/realaskaer/attackmachine
- Referral Address: 0x000000a679C2FB345dDEfbaE3c42beE92c0Fb7A5
- Modules and Strings:
	- README.md - 254
	- modules/onmichain/l2pass.py - 106
	- modules/onmichain/nogem.py - 115
	- modules/onmichain/rocketsam.py - 45
	- modules/onmichain/zerius.py - 111
	- modules/others/zkstars.py - 34
	- modules/swaps/oneinch.py - 40
	- modules/swaps/openocean.py - 26
	- modules/swaps/rango.py - 49
	- modules/swaps/xyfinance.py - 42

**Software 3: Base by Atorasi**

- Total Wallets Identified: 881
- Sybil Wallets Identified: 881
- Repository: https://github.com/atorasi/base
- Referral Address: 0x6b44f3c60a39d70fd1a168ae1a61363d259c50f0
- Modules and Strings:
	- base-main/src/swap/oneinch.py - 28
	- base-main/src/nft/zkstars.py - 31

**Software 4: Scroll_V2 by Rgalyeon**

- Total Wallets Identified: 512
- Sybil Wallets Identified: 473
- Repository: https://github.com/rgalyeon/scroll_v2
- Referral Address: 0xE022adf1735642DBf8684C05f53Fe0D8339F5663
- Modules and Strings:
	- scroll_v2/modules/zkstars.py - 36

**Software 5: Scroll Automation by 3easyPe**

- Total Wallets Identified: 50
- Sybil Wallets Identified: 50
- Repository: https://github.com/3asype/scroll-automation
- Referral Address: 0x00000D01B969922762a63F3cfD8ec9545DE4d513
- Modules and Strings:
	- scroll-automation-main/modules/xyswap.py - 65

After merging all lists and removing duplicates, the total list was reduced to 52,621 Sybil wallets (52,676 unfiltered).

# Detailed Methodology & Walkthrough

1. Downloaded all transaction history from these wallets via https://docs.cloud.debank.com/en/readme/api-pro-reference/user#get-user-transaction-history-on-all-supported-chains.
2. In the output CSV file extracted all ‘from_addr’ EVM addresses and ‘action’ parameters from the ‘tx’ column (JSON) into separate columns.
3. Created a deduplicated list of ‘from_addr’ in a ‘wallets.xlsx’ file.
4. Removed wallets that have been found in the provided by LayerZero blacklist.
5. Added a column ‘transactions’ and filled it with transaction counts from the provided snapshot for each wallet.
6. Added a column 'balance' by scraping wallet balances in USD across all blockchains from DeBank using Octoparse.
7. Added a column 'interacted projects' and listed all swap-type projects that wallets have interacted with, separated by commas.
8. Added a column 'wallet label' by scraping wallet labels from Arkham Intelligence using Octoparse to reveal address identities.
9. Added a column ‘software interactions’, showing the number of wallet interactions with the referral address through the software on all blockchains, which confirms repeated activity of Sybil wallets. Please note that it doesn’t show the full amount of software interactions, as it’s limited to projects where referral address was used.
10. Added a column ‘actions’ and listed, separated by commas, all types of actions (‘mint’, ‘safeMint’, etc.) that were found for each wallet address.
11. Compiled a list of unique actions that were found, uploaded all Python modules that had referral codes (such as modules/onmichain/l2pass.py) in ChatGPT, and asked AI to identify which actions could trace them back to being referrals from using the software. In addition, the accounts' transaction histories were reviewed in DeBank, and actions were manually validated to confirm and adjust filters (see ‘action_filters.png’).
12. In total, the following filters were applied:
	- 'transactions' > 0 - removes wallets that haven't interacted with LayerZero
	- 'blacklist' = 'none' - removes wallets that have been marked as Sybils by LayerZero   
	- 'actions' = 'safeMint', 'mint', 'swap', 'swapCompact', ‘onChainSwaps', ‘0’ (optional), ‘blank’ (optional) - filters out ‘iRelay’, ‘multicall’, ‘airdrop’, etc.
13. Identified:
	- 45,404 Sybil wallets from CZBag
	- 9,383 Sybil wallets from RealAskaer
	- 881 Sybil wallets from Atorasi
	- 473 Sybil wallets from Rgalyeon
	- 50 Sybil wallet from 3asyPe
14. Additionally, to validate the high quality of this research:
	- A manual review of DeBank's transaction history was conducted on referral addresses and a portion of the identified addresses with different sets of actions to validate results.
	- Actions '0' (54 wallets) and 'blank' (4,579 wallets) are optional, as specified in point 12. They have been added due to the high number of software interactions. '0' actions are from interactions on the Scroll blockchain from software #5, while all 'blank' are from swap-type actions on 'xyfinance.'
	- A deep analysis of 'interacted projects' data proved that there are no P2P transactions involved in swap-type actions. This is because the majority of wallets have interacted with multiple projects (non-referrals wouldn’t be able to do so), and even if they have interacted with only one project, they have multiple software interactions and low wallet balances. However, if LayerZero insists, swap-type actions can either be filtered out completely, or the minimum number of software interactions required for them to be shortlisted can be increased. For this purpose, an ‘action_filter.py’ script was developed that works based on the number of software interactions entered in the 'action_filter' tab of ‘full_data.xlsx’. After setting values and launching the script, wallets will be filtered based on the set threshold of software interactions for each action. Mint-type actions can have at least 1 interaction, while for swap-type actions, it can be set to 2-3.
	- An additional analysis of ‘software interactions’ data was conducted to evaluate how intensely software was used and how filtered list will be reduced if we count:
		- 1 or more interactions: 52,621 wallets
		- 2 or more interactions: 37,339 wallets
		- 3 or more interactions: 25,546 wallets
		- 10 or more interactions: 6,923 wallets
		- 20 or more interactions: 2,091 wallets
	- The average balance per wallet is approximately $200, with 2% of shortlisted wallets exceeding $1,000, 7.5% exceeding $500, and the maximum being over $150,000 with almost 250 transactions. It is assumed that software is used to farm transactions on main wallets in addition to the secondary ones, so they were not filtered out. However, LayerZero may choose to filter out wallets with balances under $1,000 or $500 to limit the final list to the secondary wallets.
	- Attempts were made to pull the average and maximum values of all transactions for each Sybil wallet to confirm that all transactions weren't too large to be validated as referral fees. However, due to technical limitations, the transaction value in USD could be retrieved for only 20% of transactions, and all of these appear to be referral fees. Due to other verifications confirming that these are Sybil wallets, this percentage, along with the absolute results, can be considered sufficient to verify the findings in addition to other methods.
	- 99% of Sybil wallets were extracted from addresses used solely as referral addresses in the Sybil software (others were meticulously filtered out), which simplifies analysis, maximizes accuracy, and excludes all non-Sybil users.

A full list of 52,676 wallets will be provided in the file 'full_data.xlsx' so that the LayerZero team can apply filters based on the provided options, such as filtering by different 'action' parameters, 'balance,' ‘software interactions,’ or by adding their own data points. Please make the final decision on how they should be filtered out based on your conclusions from the provided information.

My suggestion is to mark 52,621 wallets from 'reported_addresses.csv' as Sybils. However, this is the maximum number that can be added based on the done research, and it can be decreased if LayerZero finds it appropriate.

All files: https://mega.nz/folder/d6cmCC4a#-NItXmRJqGYZ1zT4TmZ5iA

# Reward Address (If Eligible)

0x1b56295F65c838a864AE87C8085cb836314c6420
