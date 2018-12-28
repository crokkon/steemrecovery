# SteemRecovery
A python CLI to recover Steem accounts.

Notes:
* If the account to be recovered was created via https://steemit.com then this tool is (probably) not suited for you. In this case, please follow the [Stolen Accounts Recovery](https://steemit.com/recover_account_step_1) instructions from Steemit.
* Prefer a JavaScript solution? Check the [SteemAccountRecovery](https://github.com/CodeBull/SteemAccountRecovery) tool from @CodeBull.

## Features

* Calculate new keys from a random or given master password
* Request and perform the recovery of Steem accounts
* Analyze accounts for possible hack left-overs
  * detect and stop power-downs
  * find and remove withdraw routes
  * find and cancel requests to change the recovery partner
* Support for custom Steem node URLs and Steem forks via the `--node [URL]` parameter
* Test commands in `--dry-mode` without sending any operations to the chain

The recovery of Steem accounts requires action from both the owner of the account to be recovered as well as the corresponding recovery account owner. This tool is targeted towards account creators and users who need recovery tools for own accounts or accounts created for others.


## How does the Steem account recovery process work?

As for every other crypto, whoever owns the private keys owns the account and the funds stored there. Steem is no exception there, but provides an option to recover the ownership of an account in case the keys got leaked/phished/lost. The recovery process requires the account owner to know an owner key or a master password which was the valid key/password somewhen within the last 30 days. Additionally, the recovery process has to be initiated from the recovery partner of the account to be recovered. It is the responsibility of the recovery partner to ensure that the person asking for recovery is the original owner of the account to be recovered. The recovery process then consists of 3 steps:

1) The owner of the account to be recovered generates a new set of keys for the account.
2) The recovery partner requests the recovery of the account to be recovered with the publich owner key from step 1.
3) The owner of the account to be recovered can now recover the account with the help of both the old and the new owner key.

Note that an account recovery cannot undo or revert any transfers, posts, comments or votes.


## Installation

```
pip install -U steemrecovery
```

Steemrecovery requires [beem](https://github.com/holgern/beem) >= v0.20.14.


## Usage

### Step 1: Create new keys
* **Who**: The owner of the to-be-recovered account
* **Keys** needed: none

```
$ steemrecovery suggest-keys [to-be-recovered-account]
```

Sample output (no real keys):
```
$ steemrecovery suggest-keys stmdev

1.) Store the new master password and keys safely!
+-----------------------------+------------------------------------------------------+
|       New PRIVATE keys      |       DO NOT PUBLISH OR FORWARD, STORE SAFELY!       |
+-----------------------------+------------------------------------------------------+
|           Account           |                        stmdev                        |
| New private master password | P5Jzy3gUnXvfLs112KdP9tMiPaxvTL6QqiijhZ96APwsRGnmnN3L |
|    New private active key   | 5JygJLgFueQoWWD8jjCUgtAHPJZhpvnpPHk63Y4C8hF6oUh35f7  |
|   New private posting key   | 5JcNkf34weeuN39pUFEYtMjmmcx5MJBWZ3eecpAAggVFU3kUgj3  |
|     New private memo key    | 5KC9nyuCjXKufrea3NET77B68vLBqL1qPMisJq7zKjyE51tKBMC  |
+-----------------------------+------------------------------------------------------+

2.) Make sure you stored the new password and keys safely!

3.) Forward the new PUBLIC owner key to your recovery account:
+----------------------+-------------------------------------------------------+
| New PUBLIC owner key |         Forward this to your recovery partner         |
+----------------------+-------------------------------------------------------+
|       Account        |                         stmdev                        |
| New public owner key | STM6ATH8dXQVUMi6rmfTYW66SZQfHGX9uyJ4YZQaJMidgxVYamdTu |
+----------------------+-------------------------------------------------------+
```
Store the private master password and all private keys safely, don't publish or forward those! Forward only the new **PUBLIC** owner key to the recovery partner


### Step 2: Request the account recovery
* **Who**: The owner of the corresponding recovery account
* **Keys needed**: Active key of the recovery account

This command asks for the new **public** owner key from step 1.

```
$ steemrecovery request-recovery [account_name]
```

Sample output:
```
$ steemrecovery request-recovery stmdev
Enter new PUBLIC owner key for @stmdev: STM6ATH8dXQVUMi6rmfTYW66SZQfHGX9uyJ4YZQaJMidgxVYamdTu
Enter active key, owner key or master password for @crokkon:
INFO: @crokkon requested account recovery for stmdev
```


### Step 3: Recover the account
* **Who**: The owner of the to-be-recovered account
* **Keys needed**: The old and the new owner key or master password

```
$ steemrecovery recover-account [account_name]
```

Sample output:
```
$ steemrecovery recover-account stmdev
Enter the old master password or owner key for @stmdev:
Enter the new master password for @stmdev:
INFO: @stmdev recovered.
INFO: @stmdev's active, posting and memo keys updated.
```

## Analyze for hack left-overs

* **Who**: The owner of the recovered account
* **Keys needed**: The analysis needs no keys. The Countermeasures need owner or active keys, or the master password.

```
$ steemrecovery analyze [account_name]
```

Detects:
* Recovery account change requests
* Power-downs
* Vesting withdraw routes (e.g. STEEM ending up in another account after a power-down)

Sample Output:
```
$ steemrecovery analyze stmdev
INFO - Last owner update: 2018-11-11 22:09:48+00:00 (26 days ago)
INFO - Recovery account: crokkon
WARNING - Account is currently powering down:
WARNING - Next vesting withdrawal: 154.648882 VESTS (~0.077 STEEM) at 2019-01-04 08:58:33+00:00
WARNING - Account has withdraw routes set:
+--------+---------+---------+-----------+
|  From  |    To   | Percent | Auto-vest |
+--------+---------+---------+-----------+
| stmdev | crokkon |  100.0  |   False   |
+--------+---------+---------+-----------+
WARNING - Request to change the recovery account to @crokkon, will be effective on: 2019-01-27T09:07:06
```

### Countermeasures

* Stop power-down
```
$ steemrecovery stop-powerdown [account_name]
```

* Cancel recovery account change requests:
```
$ steemrecovery cancel-recovery-account-change [account_name]
```

* Remove withdraw vesting routes
```
$ steemrecovery remove-withdraw-vesting-routes [account_name]
```

## Roadmap
* Implement support for non-trivial recent owner authorities
* Test on Steem forks

## Contributing
PRs are welcome! Please ensure pyflakes/pep8/flake8 compatibility.
