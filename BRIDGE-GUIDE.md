# How to Get OKB Gas on X Layer Mainnet

We need a tiny amount of OKB (~$0.01 worth) for verdict transactions on X Layer mainnet.

## Option 1: OKX Official Bridge (EASIEST if you have OKX account)
1. Go to https://www.okx.com/xlayer/bridge
2. Select Ethereum → X Layer
3. Bridge ETH (even $1 worth)
4. ETH arrives on X Layer — swap a tiny bit to OKB on OKX DEX
5. Or just use ETH directly — X Layer accepts ETH for gas too!

## Option 2: Rhino.fi (EASIEST from MetaMask)
1. Go to https://app.rhino.fi/bridge/
2. Connect MetaMask
3. Source: any chain you have funds on (Ethereum, Base, Arbitrum, etc.)
4. Destination: X Layer
5. Token: ETH or USDC
6. Amount: even $1 is enough for hundreds of verdict txs
7. Fee: ~0.19% + gas
8. Arrives in ~2 minutes

## Option 3: OKX Wallet Swap (if you have OKX Wallet)
1. Open OKX Wallet
2. Swap any token to X Layer
3. Direct bridge built into the wallet

## Option 4: MetaMask Portfolio Bridge
1. https://portfolio.metamask.io/bridge
2. Select source chain → X Layer (Chain ID 196)
3. Bridge ETH/USDC

## Our Wallet
```
0x2BfCa9397CE1E04B1A9B3575F5A957c5d58fd45d
```

## Gas Math
- One verdict tx: ~28,840 gas
- 4 verdicts per session: ~115,360 gas
- Gas price: ~0.000000025 OKB (25 gwei)
- Cost per session: ~0.000003 OKB ≈ $0.00015
- **$1 of OKB = ~6,600 tribunal sessions**

We literally need dust.

## IMPORTANT
- X Layer mainnet Chain ID: 196
- RPC: https://rpc.xlayer.tech
- Native token: OKB (used for gas)
- Explorer: https://www.okx.com/web3/explorer/xlayer

## Quick Check Balance
```bash
python3 -c "from web3 import Web3; w3 = Web3(Web3.HTTPProvider('https://rpc.xlayer.tech')); print(f'{w3.from_wei(w3.eth.get_balance(\"0x2BfCa9397CE1E04B1A9B3575F5A957c5d58fd45d\"), \"ether\")} OKB')"
```
