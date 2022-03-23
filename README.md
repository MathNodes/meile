# Meile (may•lah)
A Sentinel Network dVPN TUI client. 

## Dependencies
![sentinel-cli](https://github.com/sentinel-official/cli-client)

## Installation (Linux)

Install python dependencies
```shell
pip install npyscreen requests configparser pkg_resources curses
```

Create a config folder
```shell
mkdir -p $HOME/.meile
```

Clone repo & copy config.ini
```shell
mkdir -p $HOME/git && cd $HOME/git && \ 
git clone https://github.com/MathNodes/meile && \
cp $HOME/git/meile/config.ini $HOME/.meile
```

Run
```shell
cd $HOME/git/meile && python3 meile.py
```

It will prompt you or your Wallet Name and Wallet Address. 
Meile will store this information in the `$HOME/.meile/config.ini` for future processing.

## Notes
More to come. This is a beta release. It will be packaged as a pip package for official release. Please address all issues in the **issues** section of this repo. We will work
to fix any issues or add enhancments people may suggest. 

## Tipjar
You tip a waiter/waitress for their service, why not tip a programmer for their code?

### Sentinel (dvpn)
```shell
sent1hfkgxzrkhxdxdwjy8d74jhc4dcw5e9zm7vfzh4
```

### Monero (xmr)
```shell
8A8TesuUctMQzq1oNM5VWQeZxu5SPDQyf87yMUdvPfSxjXQKvZSY3F7Dm9zGD3uKXbQ6ZMXGRydyQAGGQvBSfeVZBtJxh8A
```




