# Cardano Node Role

![Ansible Lint](https://github.com/grzegorznowak/cardano-node-role/actions/workflows/lint.yml/badge.svg)
![CI Sources Integration](https://github.com/grzegorznowak/cardano-node-role/actions/workflows/ci-sources.yml/badge.svg)
![CI Binary Integration](https://github.com/grzegorznowak/cardano-node-role/actions/workflows/ci-prebuilt.yml/badge.svg)

Installs Cardano Node as a systemd service on Ubuntus and Debians.
Then wraps it with Ansible tortilla to make certain ops controllable, idempotent and way simpler in general.

Can add and integrate [CNCLI](https://github.com/AndrewWestberg/cncli) when directed to.

## Supported Distros

Adoption and support of more distributions will greatly depend on the users' feedback.

Please add your use cases to the issue tracker and we will triage those as we go.

### Ubuntu

* 20.04
* 18.04
### Debian

* bullseye

## Installation ##

one of:
* `ansible-galaxy install grzegorznowak.cardano_node`
* clone the repo directly

## Example playbook 

There are 2 main modes of installation:
* Compilation from source
* Using pre-built dist binaries from IOHK

controllable with the `cardano_install_method` flag. 
See the `Configuration` section further down.

Binary dist install should generally fit most of the cases, but go ahead and use src to unlock the ultimate nerd-build.
 
This role attempts to test both of the approaches.
 
##### When cloned from github

```YAML
- name: Converge Cardano Node
  hosts: all
  vars:
    cncli_add: true  # will include CNCLI
    cardano_wallets:  # will create two wallets for you
      - savings
      - operations
  roles:
    - cardano-node-role
```        
##### When installed with ansible-galaxy

```YAML
- name: Converge Cardano Node
  hosts: all
  vars:
    cncli_add: true  # will include CNCLI
    cardano_wallets:  # will create two wallets for you
      - savings
      - operations
  roles:
    - grzegorznowak.cardano_node
```        

## Configuration & Usage

By default installs cardano for a `cardano` user and group. Which is a recommended practice. 
All other cogs to fiddle with can be found under `defaults/main.yml`. 

More detailed usage examples and copy-pasteable commands will be arriving with subsequent sprints.

### Payment Addresses

We can keep track of ADA addresses at our disposal.

**NOTE: This role doesn't (yet) integrate any sort of wallet software. What we do is creating needed files to 
send and receive payments using cli commands. "Wallet" in this context means a named path that holds files belonging
together**

The current approach is to only create wallets that do not exist, as well as report
if it finds ones that are broken - ie. missing private keys. 
For security reasons we will not try to delete existing wallets,
even though this stands opposite to the ansible philosophy of defining 
and converging to specified state of the system. 
 
```yaml
# populate with a list wallet names you wish to track with the role
cardano_wallets:
  - savings
  - operations
```

Based on the sample above - assuming all default values are used - materialized wallet addresses will be located under: 

* `/home/cardano/wallets/savings/payment.addr`
* `/home/cardano/wallets/operations/payment.addr`

alongside wallets' private keys

### Node Sync Status Assertion

Block execution of a playbook until cardano node is fully synced.

```
- name: Wait until we are fully synced
  assert_cardano_synced:
    cardano_node_socket: "{{ cardano_node_socket }}"
    cardano_bin_path: "{{ cardano_bin_path }}"
    active_network: "{{ active_network }}"
    testnet_magic: "{{ network_magic }}"  # only used on testnet
  retries: 60
  delay: 240    # wait up to 4h for full sync
  become: true
  become_user: "{{ cardano_user }}"
  register: sync_check_result
  until: sync_check_result.progress | int == 100

```

### Funds Assertion

Make sure the specific address has at least the given amount of Ada at it's disposal.
Useful for monitoring a service that has to have some Ada all times, or
blocking specific Ops that require certain amounts to be available.

```
- set_fact
      wallet_to_check: default
      lovelace_needed: 1000000000

- name: Collect wallets
  cardano_wallet:
    cardano_bin_path: "{{ cardano_bin_path }}"
    name: "{{ wallet_to_check }}"
    active_network: "{{ active_network }}"
    testnet_magic: "{{ network_magic }}"  # only used on testnet
  become: true
  become_user: "{{ cardano_user }}"
  register: wallet_results

- name: Make sure we have some Lovelace
  assert_address_funded:
    cardano_node_socket: "{{ cardano_node_socket }}"
    cardano_bin_path: "{{ cardano_bin_path }}"
    active_network: "{{ active_network }}"
    testnet_magic: "{{ network_magic }}"  # only used on testnet
    expected_lovelace: "{{ lovelace_needed }}"
    address: "{{ wallet_results['wallets_addresses'][wallet_to_check] }}"    
  retries: 60
  delay: 240    # wait up to 4h for full sync
  become: true
  become_user: "{{ cardano_user }}"
  register: lovelace_result
  until: lovelace_result.lovelace | int > lovelace_needed
```

### Native Tokens

Idempotently mint native tokens (not NFTs) with this role.
It will not re-attempt to mint the token if it's already
present and in the wanted quantity under the payment address specified.

At this point minted tokens are sent to the wallet used for minting.   

Minimal config needed on mainnet:
```
cardano_install_method: dist
active_network: main
cardano_wallets:
  - &wallet_default default
cardano_assets:
  - name: MyAsset
    quantity: 1000000
    wallet: *wallet_default  
```

### General Settings

```yaml
# Cardano user
cardano_home_directory: /home/cardano
cardano_user: cardano
cardano_group: cardano

# possible options:
# src - compile from source
# dist - use the official binary
cardano_install_method: src

# Version variables
ghc_version: 8.10.4
cabal_version: 3.4.0.0

# Applicable only when building from src
cardano_node_version: 1.30.0

# Applicable only when installing from dist
cardano_hydra_build: 7981360
# always confirm your sha, or a poison might be coming
cardano_dist_sha_256: 3bf8dae2457e647600180ceda094637b46bcab9da837c769d6e8c9e3e8dc157c
cardano_dist_url: "https://hydra.iohk.io/build/{{ cardano_hydra_build }}/download/1"

# Service Config
cardano_listen_addr: 127.0.0.1
cardano_listen_port: 22322  # has to be in the upper bracket if it's running as non-privileged user

# CNCLI config
cncli_add: false  # set to 'true' to enable cncli with cncli-sync service 
``` 

There's more, so head on to the `defaults/main.yml` file directly to see all the little details.

### Cardano CLI

One of the end goals of this repository is to abstract cardano Ops with ansible tasks,
but there is no stopping you to interact with services and binaries directly.


```shell script
su cardano
cd ~/bin
./cardano-cli --help
```

For usage details go to [cardano-cli documentation](https://github.com/input-output-hk/cardano-node/tree/master/cardano-cli) directly

### CNCLI

For usage details see the [original repository](https://github.com/AndrewWestberg/cncli/blob/develop/USAGE.md)

## Managing Services

Use it as any other service
```shell script
# managing the cardano-node process:
systemctl status cardano-node
systemctl restart cardano-node

# looking at general logs
journalctl -u cardano-node
```

Interacting with CNCLI sync service, when it's enabled
```shell script
# managing the cncli-sync process
systemctl status cncli-sync
systemctl restart cncli-sync

# looking at general logs
journalctl -u cncli-sync
```


## Integration Testing

### locally on LXD

LXD should already be installed and configured.

Trigger the full suite with `./test-local.sh`

Compilation of the required binaries is a CPU heavy task, so be prepared for a long-haul process.

### on Cloud via CI pipeline

CI built on top of DO infrastructure and getting triggered against every meaningful changeset in the `main` branch.

To limit running costs the from-source CI done against Focal Fossa only atm.

The pre-built binary CI done against focal and bionic.

The other supported platforms are being assessed locally.


## Motivation

This role is a rolling exploration of cardano backend and services' configuration, with functionality
that will grow over time as we understand the search-space better.

Brewed using high TDD and coding standards, making sure changes don't break any of the existing components. 

**Remember to always ask for tests when ordering your ansible pizza.** 

#### When should I use this role over the official docker image ?

First of all docker is a great tool that I leverage in my projects a tonne to provide consistent images for concrete 
tasks. The specificity of docker comes with a price and that is it's **not fun when it comes to networking or systemd**. 
On it's own it can't really do any of those things full-on and thus behold kubernetes, docker-swarms et al.
Which is perfectly fine until you need to actually do a bespoke setup with mesh VPN or live services monitoring - 
you start adding layer after layer of complexity to the system only to solve problems that docker itself brought; 
with lots dependencies that are not easy to deploy with **infra-as-code** principle. 
  
If I learnt anything over the years in development, is that there is truly no solution that fits it all.
At some point when a production grade platform is considered, trying to shoe hone docker into the frames 
of correctly defined and controlled environment is just much more work than compiling a well understood and minimal
set of roles that provide specific value. 

If you're not developing the system with docker first approach, which I personally find really a roundabout fashion
eventually, then you might enjoy this role. With an added value of being **perfectly transparent**; so you're never 
worried what your docker image comes with prepackaged other than what it claims.

Initial tests were conducted using lxd containers, which are flyweight, fast and native to ubuntu, and can 
simulate actual servers on a level that docker really can't. 

### Noteworthy

Thanks to Molecule we're currently in the era of test-driven-infra-as-code. 
Which this project is a manifestation of too.
So please head on to https://github.com/ansible-community/molecule and give it some love and attention.

## Target audience

Developers and Ops

## Roadmap

The project is rolled with [weekly sprints](https://github.com/grzegorznowak/cardano-node-role/projects).
Have a look there to see what's currently being worked on.

The very broad 10k feet view of what is planned generally:
* ~~A baseline Cardano Node installation~~
* ~~Full CI/CD~~
* ~~Integrate CNCLI~~
* Automate native tokens minting
* Automate NFT minting
* Smart contracts' interfacing 
* More/better provisioning examples
* Exposition of what would be the result of running this role as a public node
* ~~Automation of keys management~~

Some food for thought, but not really in plans as of now:
* Research the possibility of Block Producing Node to be ephemeral
* Complete stacking pool implementation  

the above is subject to change or can be refactored into bespoke roles for modularity.
 
## Donations

Running CI pipeline for this project is no fluff, so your support is highly appreciated

You can support this project by buying a native token minted using this very role and called a `FKL`,
which pays tribute to Guy Richie's movies.

Simply Send 2ADA to the following address and I will send you 1FKL + ~1.5ADA back, fees excluded. 

`addr1q8ckqv8hm9zsvv8glxypmj3chfymjttnppfeypgt4zy09p6nzz27ada3sl2vhc30j64g2j6788fkqx4cqmgzxvxxyurs479zqu`
