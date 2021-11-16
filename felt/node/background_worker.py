import asyncio

import websockets
from web3 import Web3

from felt.node.utils.contracts import load_contracts

# Connect to application running on this server itself and coordinate tasks
URL = "ws://localhost:8000/training/ws"
ETH_NODE = "http://127.0.0.1:8545"


async def producer(federated_contract):
    await asyncio.sleep(3)
    return "p"


async def task():
    w3 = Web3(Web3.HTTPProvider(ETH_NODE))
    print("Chain id", w3.eth.chain_id)
    contracts = load_contracts(w3.eth.chain_id)
    for k, c in contracts.items():
        contracts[k]["obj"] = w3.eth.contract(address=c["address"], abi=c["abi"])

    print("Fee:", contracts["ContractManager"]["obj"].functions.activationFee().call())
    # Infinite reconnect + run infinite connection - lovely :)
    while True:
        async with websockets.connect(URL) as websocket:
            try:
                while True:
                    cmd = await producer()
                    # Request plan pull
                    await websocket.send(cmd)
                    rec = await websocket.recv()
                    print("Received")

            except websockets.ConnectionClosed:
                continue


def main():
    asyncio.run(task())


if __name__ == "__main__":
    main()
