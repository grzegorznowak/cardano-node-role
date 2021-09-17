# Cardano Node Role

Installs Cardano Node as a systemd service on Ubuntus and Debians.

Currently builds and integrates on:
##### Ubuntu: 20.04, 18.04
##### Debian: bullseye
 
Please note this is an early version of documentation.

## Integration Testing

### locally on LXD

python3 and LXD should be already installed and configured.

Trigger the full suite with `./test-local.sh`

Compilation of the required binaries is a CPU heavy tasks, so be prepared for a long-haul process.

### on Cloud via CI pipeline

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

#### When should I use this role over the official docker image ?

First of all docker is a great tool that I leverage in my projects a tonne of to provide consistent images for concrete 
tasks. The specificity of docker comes with a price and that is it's not fun when it comes to networking or systemd. 
On it's own it can't really do any of those things full-on and thus behold kubernetes, docker-swarms et al.
Which is perfectly fine until you need to actually do a bespoke setup with mesh VPN or live services monitoring - 
you start adding layer after layer of complexity to the system only to solve problems that docker itself brought, 
with lots dependencies, that are not easy to deploy with infra-as-code principle. 
  
If I learnt anything over the long years in development, is that there is truly no solution that fits it all.
At some point when a production grade platform is considered, trying to shoe hone docker into the frames 
of correctly defined and controlled environment is just much more work than compiling a well understood and minimal
set of roles that provide specific value. 

If you're not developing the system with docker first approach, which I personally find really a roundabout fashion
eventually, then you might enjoy this role. With an added value of being perfectly transparent; so you're never 
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

* ~~A baseline Cardano Node installation~~
* Full CI/CD
* More/better provisioning examples
* Exposition of what would be the result of running this role as a public node
* Automation of keys management
* Complete stacking pool implementation  

 
## Donations

##### RVN wallet
`RKcFiQxRpUv6GTVSX7HQZc4EA5jAKPkVNV`

##### ADA wallet
`addr1q8ckqv8hm9zsvv8glxypmj3chfymjttnppfeypgt4zy09p6nzz27ada3sl2vhc30j64g2j6788fkqx4cqmgzxvxxyurs479zqu`