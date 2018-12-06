# Steem Account Recovery with Beem

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

Forward the new **PUBLIC** owner key to the recovery partner


### Step 2: Request the account recovery
* **Who**: The owner of the corresponding recovery account
* **Keys needed**: Active key of the recovery account

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
$ steemrecovery recover-account.py [account_name]
```

Sample output:
```
$ steemrecovery recover_account stmdev
Enter the old master password or owner key for @stmdev:
Enter the new master password for @stmdev:
INFO: @stmdev recovered.
INFO: @stmdev's active, posting and memo keys updated.
```
