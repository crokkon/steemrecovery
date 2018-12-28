from __future__ import print_function
import click
import logging
import sys
from beem import Steem
from beem.blockchain import Blockchain
from beem.instance import set_shared_steem_instance
from beem.transactionbuilder import TransactionBuilder
from beem.utils import addTzInfo
from beemgraphenebase.account import PasswordKey, PrivateKey, PublicKey
from beembase import operations
from beem.account import Account
from beem.constants import STEEM_1_PERCENT
from prettytable import PrettyTable
from getpass import getpass
from datetime import datetime
from steemrecovery.version import VERSION


# map input to raw_input for Python2
if hasattr(__builtins__, 'raw_input'):
    input = raw_input

verbosities = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
time_unset = [addTzInfo(datetime.utcfromtimestamp(0)),
              addTzInfo(datetime.utcfromtimestamp(-1))]
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s - %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


def passwordkey_to_key(passwordkey, account, role, prefix="STM"):
    """ Get a private key from an input that may be a key or a master
    password.

    :param str passwordkey: Key or master password to check/transform.
    :param str account: Account name the key is for.
    :param str role: Role of the key (posting, active, owner, memo)
    :param str prefix: Network prefix (default: "STM")

    """
    try:
        # check if passwordkey is a valid private key
        PrivateKey(passwordkey, prefix=prefix)
        return passwordkey
    except ValueError:
        # PrivateKey() failed, provided string is not a private key
        # -> treat it as a master password
        pk = PasswordKey(account, passwordkey, role=role,
                         prefix=prefix)
        return str(pk.get_private())


@click.group(chain=True)
@click.option('--node', '-n', default="", help="Custom node URL.")
@click.option('--dry-run', '-d', default=False, is_flag=True,
              help="Dry run, don't broadcast any transaction.")
@click.option('--verbosity', '-v', type=click.Choice(verbosities),
              default='INFO', help="Verbosity (default: INFO).")
@click.version_option(version=VERSION)
def cli(node, dry_run, verbosity):
    numeric_loglevel = getattr(logging, verbosity.upper(), None)
    if not isinstance(numeric_loglevel, int):
        raise ValueError('Invalid log level: %s' % verbosity)
    logger.setLevel(numeric_loglevel)
    stm = Steem(node=node, nobroadcast=dry_run)
    set_shared_steem_instance(stm)


@cli.command()
@click.argument('account')
def analyze(account):
    """Analyze ACCOUNT for possible hack leftovers.

    """
    acc = Account(account.replace("@", ""))
    if acc['last_owner_update'] not in time_unset:
        days = (addTzInfo(datetime.utcnow()) - \
                acc['last_owner_update']).days
        last_update = "%s (%d days ago)" % (acc['last_owner_update'],
                                            days)
    else:
        last_update = "never"
    logger.info("Last owner update: %s" % (last_update))
    logger.info("Recovery account: @%s" % (acc['recovery_account']))

    # check if the account is currently powering down

    if acc['next_vesting_withdrawal'] not in time_unset:
        vests = acc['vesting_withdraw_rate']
        sp = acc.steem.vests_to_sp(vests.amount)
        logger.warning("Account is currently powering down:")
        logger.warning("Next vesting withdrawal: %s (~%.3f %s) at %s" %
                       (vests, sp, acc.steem.steem_symbol,
                        acc['next_vesting_withdrawal']))
    else:
        logger.info("Account is not powering down.")

    # check for active withdraw vesting routes
    routes = acc.get_withdraw_routes()
    if len(routes):
        tbl = PrettyTable(['From', 'To', 'Percent', 'Auto-vest'])
        for route in routes:
            tbl.add_row([route['from_account'], route['to_account'],
                         int(route['percent']) / STEEM_1_PERCENT,
                         route['auto_vest']])
        logger.warning("Account has withdraw routes set:\n" + str(tbl))
    else:
        logger.info("Account has no withdraw routes set")

    bc = Blockchain()
    requests = bc.find_change_recovery_account_requests([account])
    if len(requests):
        logger.warning("Request to change the recovery account to "
                       "@%s, will be effective on: %s" %
                       (requests[0]['recovery_account'],
                        requests[0]['effective_on']))
    else:
        logger.info("No pending requests to change the recovery account")


@cli.command()
@click.argument('account')
@click.argument('new_recovery_account')
def change_recovery_account(account, new_recovery_account):
    """ Change the recovery account of ACCOUNT to NEW_RECOVERY_ACCOUNT.

    """
    acc = Account(account.replace("@", ""))
    # Account() lookup to ensure that the account exists
    new_rec = Account(new_recovery_account)
    logger.info("About to change recovery account of @%s from %s to %s" %
                (acc['name'], acc['recovery_account'], new_rec['name']))
    pwd = getpass("Enter master password or owner key for @%s: " %
                  (acc['name']))
    pk = passwordkey_to_key(pwd, acc['name'], role="owner",
                            prefix=acc.steem.prefix)
    acc.steem.wallet.setKeys([pk])
    tx = acc.change_recovery_account(new_rec)
    logger.debug(tx)
    logger.info("Recovery account change request to @%s will be active " \
                "in 30 days" % (new_rec['name']))


@cli.command()
@click.argument('account')
def cancel_recovery_account_change(account):
    """ Cancel a pending recovery account change request for ACCOUNT.

    """
    acc = Account(account.replace("@", ""))
    bc = Blockchain(steem_instance=acc.steem)
    req = bc.find_change_recovery_account_requests(acc['name'])
    if len(req) == 0:
        logger.error("Could not find a pending recovery account change "
                     "request, nothing to cancel.")
        return
    logger.info("Found recovery account change request to @%s" %
                (req[0]['recovery_account']))
    pwd = getpass("Enter master password or owner key for @%s: " %
                  (acc['name']))
    pk = passwordkey_to_key(pwd, acc['name'], role="owner",
                            prefix=acc.steem.prefix)
    acc.steem.wallet.setKeys([pk])
    tx = acc.change_recovery_account(acc['recovery_account'])
    logger.debug(tx)
    logger.info("Canceled the recovery account change request.")


@cli.command()
@click.argument("account")
def remove_withdraw_vesting_routes(account):
    """ Remove all active withdraw vesting routes from ACCOUNT.

    """
    acc = Account(account.replace("@", ""))
    routes = acc.get_withdraw_routes()
    if len(routes) == 0:
        logger.error("@%s has no withdraw vesting routes, nothing to "
                     "remove." % (acc['name']))
        return
    pwd = getpass("Enter master password or active key for @%s: " %
                  (acc['name']))
    pk = passwordkey_to_key(pwd, acc['name'], role="active",
                            prefix=acc.steem.prefix)
    acc.steem.wallet.setKeys([pk])
    for route in routes:
        tx = acc.set_withdraw_vesting_route(route['to_account'],
                                            percentage=0)
        logger.debug(tx)
        logger.info("Removed %.2f%% route to @%s" %
                    (int(route['percent'])/STEEM_1_PERCENT,
                    route['to_account']))


@cli.command()
@click.argument("account")
def stop_powerdown(account):
    """Stop power-down for ACCOUNT.

    """
    acc = Account(account.replace("@", ""))
    if acc['next_vesting_withdrawal'] in time_unset:
        logger.error("@%s is not powering down - nothing to do." %
                     (acc['name']))
        return
    pwd = getpass("Enter master password or active key for @%s: " %
                  (acc['name']))
    pk = passwordkey_to_key(pwd, acc['name'], role="active",
                            prefix=acc.steem.prefix)
    acc.steem.wallet.setKeys([pk])
    tx = acc.withdraw_vesting(0, account=acc['name'])
    logger.debug(tx)
    logger.info("Stopped power-down for @%s" % (acc['name']))


@cli.command()
@click.argument("account")
@click.option("--custom-password", "-c", default=False, is_flag=True,
              help="ask for a custom master password instead of generating "
              "a random one.")
def suggest_keys(account, custom_password):
    """Suggest a set of new keys for ACCOUNT. This should be called by the
    owner of the account to be recovered.

    """
    acc = Account(account.replace("@", ""))
    if acc.get_owner_history() == []:
        logger.warning("@%s has an empty owner history - recovering "
                       "this account won't be possible!" % (acc['name']))

    # Ask or generate a new master password
    if custom_password:
        new_password = getpass("Enter new master password for %s: " %
                               (acc['name']))
        repMasterPwd = getpass("Repeat new master password for %s: " %
                               (acc['name']))
        if new_password != repMasterPwd:
            raise ValueError("The passwords do not match!")
    else:
        new_password = "P" + str(PrivateKey(prefix=acc.steem.prefix))

    # Derive the new keys
    owner = PasswordKey(acc['name'], new_password, role='owner',
                        prefix=acc.steem.prefix)
    active = PasswordKey(acc['name'], new_password, role='active',
                         prefix=acc.steem.prefix)
    posting = PasswordKey(acc['name'], new_password, role='posting',
                          prefix=acc.steem.prefix)
    memo = PasswordKey(acc['name'], new_password, role='memo',
                       prefix=acc.steem.prefix)

    # Print results
    print("\n1.) Store the new master password and keys safely!")
    if not custom_password:
        t = PrettyTable(['New PRIVATE keys', 'DO NOT PUBLISH OR FORWARD, '
                         'STORE SAFELY!'])
        t.add_row(['Account', acc['name']])
        t.add_row(['New private master password', new_password])
        t.add_row(['New private active key', active.get_private()])
        t.add_row(['New private posting key', posting.get_private()])
        t.add_row(['New private memo key', memo.get_private()])
        print(t)

    print("\n2.) Make sure you stored the new password and keys safely!")
    print("\n3.) Forward the new PUBLIC owner key to your recovery account:")
    t = PrettyTable(['New PUBLIC owner key', 'Forward this to your '
                     'recovery partner'])
    t.add_row(["Account", acc['name']])
    t.add_row(["New public owner key", format(owner.get_public(),
                                              acc.steem.prefix)])
    t.add_row(["Recovery partner", acc['recovery_account']])
    print(t)


@cli.command()
@click.argument('account')
def request_recovery(account):
    """ Request the recovery of ACCOUNT. This action has to be
    initiated/signed by the recovery partner of ACCOUNT.

    """
    acc = Account(account.replace("@", ""))
    if acc.get_owner_history() == []:
        logger.error("The owner key of @%s was not changed within "
                     "the last 30 days - recovering this account is "
                     "not possible!" % (acc['name']))
        return

    # Ask and verify the new pubkey for the to-be-recovered account
    new_owner_key = input("Enter new PUBLIC owner key for @%s: " %
                          (acc['name']))
    # PublicKey call to make sure it is a valid public key
    pk_validity_check = PublicKey(new_owner_key, prefix=acc.steem.prefix)
    if format(pk_validity_check, acc.steem.prefix) != new_owner_key:
        raise ValueError("Invalid public owner key!")

    # Ask and verify the active key of the recovery account
    recovery_ak = getpass("Enter active key, owner key or master "
                          "password for @%s: " % (acc['recovery_account']))
    recovery_ak = passwordkey_to_key(recovery_ak,
                                     acc['recovery_account'],
                                     "active",
                                     prefix=acc.steem.prefix)

    # Assemble the account recovery request operation
    new_owner_authority = {
        'key_auths': [[new_owner_key, 1]],
        'account_auths': [],
        'weight_threshold': 1,
        'prefix': acc.steem.prefix
        }
    op = operations.Request_account_recovery(**{
        'account_to_recover': acc['name'],
        'recovery_account': acc['recovery_account'],
        'new_owner_authority': new_owner_authority,
        'extensions': [],
        'prefix': acc.steem.prefix
    })

    # Send the operation to the blockchain
    tb = TransactionBuilder(steem_instance=acc.steem)
    tb.appendOps([op])
    tb.appendWif(recovery_ak)
    tb.sign()
    tx = tb.broadcast()
    logger.debug(tx)
    logger.info("@%s requested account recovery for @%s." %
          (acc['recovery_account'], acc['name']))


@cli.command()
@click.argument('account')
def recover_account(account):
    """Recover ACCOUNT. This action has to be initiated/signed by the
    account to be recovered.

    """
    acc = Account(account.replace("@", ""))

    if acc.get_owner_history() == []:
        logger.error("@%s has an empty owner history - recovering "
                     "this account is not possible!" % (acc['name']))
        return

    # ask & verify the old owner key
    old_priv_owner_key = getpass("Enter the old master password or owner "
                                 "key for @%s: " % (acc['name']))
    old_priv_owner_key = passwordkey_to_key(old_priv_owner_key,
                                            acc['name'], role="owner",
                                            prefix=acc.steem.prefix)
    old_public_owner_key = format(PrivateKey(old_priv_owner_key,
                                             prefix=acc.steem.prefix).pubkey,
                                  acc.steem.prefix)

    # get the new password to prepare all new keys
    new_pwd = getpass("Enter the new master password for @%s: " %
                      (acc['name']))
    key_auths = {}
    for role in ['owner', 'active', 'posting', 'memo']:
        pk = PasswordKey(acc['name'], new_pwd, role=role,
                         prefix=acc.steem.prefix)
        key_auths[role] = format(pk.get_public_key(), acc.steem.prefix)
        if role == 'owner':
            new_priv_owner_key = str(pk.get_private())

    # Assemble the account recovery operation
    recent_owner_authority = {
        "key_auths": [[old_public_owner_key, 1]],
        "account_auths": [],
        "weight_threshold": 1,
        "prefix": acc.steem.prefix
        }
    new_owner_authority = {
        "key_auths": [[key_auths['owner'], 1]],
        "account_auths": [],
        "weight_threshold": 1,
        "prefix": acc.steem.prefix
        }
    op = operations.Recover_account(**{
        'account_to_recover': acc['name'],
        'new_owner_authority': new_owner_authority,
        'recent_owner_authority': recent_owner_authority,
        'extensions': [],
        "prefix": acc.steem.prefix})

    # Send the recovery operation to the blockchain
    tb = TransactionBuilder(steem_instance=acc.steem)
    tb.appendOps([op])
    tb.appendWif(new_priv_owner_key)
    tb.appendWif(old_priv_owner_key)
    tb.sign()
    tx = tb.broadcast()
    logger.debug(tx)
    logger.info("@%s recovered." % (acc['name']))

    # Assemble the account update operation
    op = operations.Account_update(**{
        "account": acc["name"],
        'active': {
            'account_auths': [],
            'key_auths': [[key_auths['active'], 1]],
            "address_auths": [],
            'weight_threshold': 1,
            'prefix': acc.steem.prefix},
        'posting': {
            'account_auths': acc['posting']['account_auths'],
            'key_auths': [[key_auths['posting'], 1]],
            "address_auths": [],
            'weight_threshold': 1,
            'prefix': acc.steem.prefix},
        'memo_key': key_auths['memo'],
        "json_metadata": acc['json_metadata'],
        "prefix": acc.steem.prefix})

    # Send the account_update operation to the blockchain
    tb = TransactionBuilder(steem_instance=acc.steem)
    tb.appendOps([op])
    tb.appendWif(new_priv_owner_key)
    tb.sign()
    tx = tb.broadcast()
    logger.debug(tx)
    logger.info("@%s's active, posting and memo keys updated."
                % (acc['name']))


if __name__ == "__main__":
    cli()
