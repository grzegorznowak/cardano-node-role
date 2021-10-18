# Cardano Node Role

![Ansible Lint](https://github.com/grzegorznowak/cardano-node-role/actions/workflows/lint.yml/badge.svg)
![CI Sources Integration](https://github.com/grzegorznowak/cardano-node-role/actions/workflows/ci-sources.yml/badge.svg)
![CI Binary Integration](https://github.com/grzegorznowak/cardano-node-role/actions/workflows/ci-prebuilt.yml/badge.svg)

Installs Cardano Node as a systemd service on Ubuntus and Debians.
Can add and integrate [CNCLI](https://github.com/AndrewWestberg/cncli) when directed to.

## Supported Distros

Adoption and support of more distributions will greatly depend on the users' feedback.

Please add your use cases to the issue tracker and we will triage those as we go.

### Ubuntu

* 20.04
* 18.04
### Debian

* bullseye
 

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

## Installation ##

one of:
* `ansible-galaxy install grzegorznowak.cardano_node`
* clone the repo directly

## Example playbook 

There are 2 main modes of installation:
* Compilation from source
* Using pre-built dist binaries from IOHK

and it's controllable with the `cardano_install_method` flag. 
See the `Configuration` section further down.
 
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

### Payment Addresses

We can keep track of ADA addresses at our disposal.

**NOTE: This role doesn't (yet) integrate any sort of wallet software. What we do is just creating needed files to 
send and receive payments using cli commands. Wallets in this context mean a named path that holds files belonging
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

### Native Tokens

#### === WIP === 
We will be able to idempotently mint native token with this role.
See the list of [weekly sprints](https://github.com/grzegorznowak/cardano-node-role/projects)
for the most up to date roadmap 

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
* More/better provisioning examples
* Exposition of what would be the result of running this role as a public node
* Automation of keys management
* Research the possibility of Block Producing Node be ephemeral
* Complete stacking pool implementation  

the above is subject to change or can be refactored into bespoke roles for modularity.
 
## Donations

Running CI pipeline for this project is no fluff, so your support is highly appreciated 

##### RVN wallet
`RKcFiQxRpUv6GTVSX7HQZc4EA5jAKPkVNV`

##### ADA wallet
`addr1q8ckqv8hm9zsvv8glxypmj3chfymjttnppfeypgt4zy09p6nzz27ada3sl2vhc30j64g2j6788fkqx4cqmgzxvxxyurs479zqu`
