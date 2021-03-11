import warnings
from collections import Counter

import toml
import requests

from brownie import chain, web3
from brownie.exceptions import BrownieEnvironmentWarning
from click import secho, style
from prometheus_client import Gauge, start_http_server
from tabulate import tabulate

from yearn import iearn, vaults_v1, vaults_v2, ironbank
from yearn.mutlicall import fetch_multicall
from yearn.constants import *

warnings.simplefilter("ignore", BrownieEnvironmentWarning)

SUCCESS_COLOR = "green"
WARNING_COLOR = "red"

DEPOSIT_LIMIT_ALERT = 85
GOVERNANCE = web3.ens.resolve("ychad.eth")
GUARDIAN = web3.ens.resolve("dev.ychad.eth")
MANAGEMENT = "0x16388463d60FFE0661Cf7F1f31a7D658aC790ff7" # Strategists ms
MGMT_FEE = 200
PERF_FEE = 1000

def safe_multifetch(contracts, attr):
  have = [c for c in contracts if hasattr(c, attr)]
  data = fetch_multicall(*[[c, attr] for c in have])
  results = {str(c): None for c in contracts}
  results.update({str(c): r for c,r in zip(have, data)})
  return results

def print_status(label, param, value):
  color = SUCCESS_COLOR
  status = "OK"

  if param != value:
    color = WARNING_COLOR
    status = "ERROR: " + param

  print(style(f"{label}", fg="blue"), style(f"{status}", fg=color))

def main():

  secho("v2", fg="cyan", bold=True)
  vaults = vaults_v2.get_vaults()
  for vault in vaults:
      ratio_color = "green"
      gov_color = "green"
      gov_status = "OK"

      info = vault.describe()
      ratio = info['totalAssets'] / info['depositLimit'] * 100
      print(f"\n{vault.name} {vault.vault.address}")
      print(style(f"Total Assets: ", fg="blue"), style(f"{info['totalAssets']:.2f}", fg="green"))
      print(style(f"Deposit Limit: ", fg="blue"), style(f"{info['depositLimit']:.2f}", fg="green"))

      if ratio > DEPOSIT_LIMIT_ALERT:
        ratio_color = "red"
      
      print(style(f"Deposit Ratio: ", fg="blue"), style(f"{ratio:.2f} %", fg=ratio_color))

      print_status('Governance', info['governance'],GOVERNANCE)
      print_status('Management', info['management'],MANAGEMENT)
      print_status('Guardian', info['guardian'],GUARDIAN)
      