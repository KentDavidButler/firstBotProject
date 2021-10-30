#!/usr/bin/env python3

import os
from azure.cli.core import get_default_cli
from dotenv import load_dotenv

load_dotenv()

SUB_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
TEN_ID = os.getenv('AZURE_TENANT_ID')
CLI_ID = os.getenv('AZURE_CLIENT_ID')
PASSWORD = os.getenv('AZURE_CLIENT_SECRET')

RESOURCE_GROUP = os.getenv('RESOURCE_GROUP')
SERVER_NAME = os.getenv('SERVER_NAME')
SERVER_NSG_NAME = os.getenv('SERVER_NSG_NAME')
NSG_RULE = os.getenv('NSG_RULE')


def az_cli(args_str):
    args = args_str.split()
    cli = get_default_cli()
    cli.invoke(args)
    if cli.result.result:
        response = cli.result.result
        return response
    elif cli.result.error:
        err_response = cli.result.error
        raise err_response
    return True


def az_login():
    login_string = f"login --service-principal -u {CLI_ID} -p {PASSWORD} --tenant {TEN_ID}"
    response = az_cli(login_string)

    return response


def az_get_nsg():
    cli_command = f"network nsg rule show --resource-group {RESOURCE_GROUP}" \
                  f" --nsg-name {SERVER_NSG_NAME} -n {NSG_RULE}"
    response = az_cli(cli_command)
    current_ip_addresses = response["sourceAddressPrefixes"]

    return current_ip_addresses


def az_set_nsg_rules(ip_list):
    try:
        print(f"****{ip_list} is not a string {type(ip_list)}")
        cli_command = f"network nsg rule update --resource-group {RESOURCE_GROUP} " \
                      f"--nsg-name {SERVER_NSG_NAME} -n {NSG_RULE} --source-address-prefixes {' '.join(ip_list)}"
        az_cli(cli_command)
        return
    except Exception as x:
        return f"Azure Exception: {x}"
