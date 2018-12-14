# SteemRecovery
A python CLI to recover Steem accounts.

Notes
* If the account to be recovered was created via https://steemit.com then this tool is (probably) not suited for you. In this case, please follow the [Stolen Accounts Recovery](https://steemit.com/recover_account_step_1) instructions from Steemit.
* Prefer a Node/JS solution? Check the recovery tools from @reazuliqbal

## Features

* Calculate new keys from a random or given master password
* Request and perform the recovery of Steem accounts
* Analyze accounts for possible hack left-overs
  * find and cancel power-downs
  * find and remove withdraw routes
  * find and cancel requests to change the recovery partner
* Support for custom Steem node URLs and Steem forks via the `--node [URL]` parameter
* Test commands in `--dry-mode` without sending any operations to the chain

The recovery of Steem accounts requires action from both the owner of the account to be recovered as well as the corresponding recovery account owner. This tool is targeted towards account creators and users who need recovery tools for own accounts or accounts created for others.


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

**Who**: The owner of the recovered account
**Keys needed**: The analysis needs no keys. The Countermeasures need owner or active keys, or the master password.

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
INFO - Account is not powering down.
INFO - Account has no withdraw routes set
INFO - No pending requests to change the recovery account
```

### Countermeasures

* Cancel recovery account change requests:
```
$ steemrecovery cancel-recovery-account-change [account_name]
```

* Remove withdraw vesting routes
```
$ steemrecovery remove-withdraw-vesting-routes
```

## Roadmap
* Implement support for non-trivial recent owner authorities
* Implement support for stopping power-downs
* Test on Steem forks

## Contributing
PRs are welcome! Please ensure pyflakes/pep8/flake8 compatibility.
