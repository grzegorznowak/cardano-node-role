# Cardano Node Role

Installs Cardano Node as a systemd service on Ubuntus and Debians.

Currently builds and integrates on those distros:

##### Ubuntu: 20.04, 18.04
##### Debian: bullseye
 
Please note this is an early version of documentation.

## Integration Testing

### locally on LXD

python3 and LXD should be already installed and configured.

Trigger the full suite with `./test-lxd.sh`

### on CI pipeline

Work in progress, tbd as soon as we understand github actions better

## Usage

```
- name: Converge Cardano Node
  hosts: all

  roles:
    - cardano-node-role
```

## Motivation

This role is meant to be a battleground for exploring cardano backend and services' configuration.

Despite being a battleground is still brewed using high TDD and coding standards, making sure 
changes don't break any of the existing components. 
Please remember to always ask for your tests when ordering your ansible pizza. 

When should I use this role over the official docker image ?

If I learnt anything over the long years in development, is that there is truly no solution that fits it all.
At some point when a production grade platform is considered, trying to shoe hone docker into the frames 
of correctly defined and controlled environment is just much more work *kuber(ekhm)netes* than compiling a well understood and minimal
set of roles that provide specific value. 

Initial tests were conducted using lxd containers, which are flyweight, fast and native to ubuntu, and can 
simulate actual servers beyond what docker can. 

### Noteworthy

Thanks to Molecule we're currently in the era of test-driven-infra-as-code. 
Which this project is a manifestation of too.
So please head on to https://github.com/ansible-community/molecule and give it some love and attention.

## Target audience

Developers and Ops

## Roadmap

* Full CI/CD
* More/better provisioning examples
* Expose what would be the result of running this role as a public node
* Complete stacking pool implementation  

 
## Donations

##### RVN wallet
`RKcFiQxRpUv6GTVSX7HQZc4EA5jAKPkVNV`

##### ADA wallet
`addr1q8ckqv8hm9zsvv8glxypmj3chfymjttnppfeypgt4zy09p6nzz27ada3sl2vhc30j64g2j6788fkqx4cqmgzxvxxyurs479zqu`