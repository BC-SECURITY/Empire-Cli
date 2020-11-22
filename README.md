**This code is in a closed beta state. There may be bugs and major changes before a full release.
Please provide feedback and bugs in the [issues](https://github.com/BC-SECURITY/Empire-Cli/issues) or in our Discord**

Empire-Cli
=============================
The new Empire CLI is a a python command-line application written using [python-prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit).
It provides many enhancements over the current CLI including:
* Support for multiple users at a time
* Custom agent shortcuts
* Enhanced autocomplete
* An interactive agent shell

- [Install and Run](#install-and-run)
- [Configuration](#configuration)
- [Usage](#usage)
	- [Main Menu](#main-menu)
	- [Admin Menu](#admin-menu)
	- [Listener Menu](#listener-menu)
	- [Use Listener Menu](#use-listener-menu)
	- [Stager Menu](#stager-menu)
	- [Use Stager Menu](#use-stager-menu)
	- [Plugin Menu](#plugin-menu)
	- [Use Plugin Menu](#use-plugin-menu)

----------------------------------

##  Install and Run
We recommend the use of [Poetry](https://python-poetry.org/docs/) for installing and running this project.
In the future, it will most likely be packaged in the main Empire repository.
```shell script
poetry install
poetry run python main.py
```

## Configuration
The Empire-Cli configuration is managed via [config.yaml](./config.yaml).

- **servers** - The servers block is meant to give the user the ability to set up frequently used Empire servers.
If a server is listed in this block then when connecting to the server they need only type: `connect -c localhost`.
This tells Empire-Cli to use the connection info for the server named localhost from the yaml.
```yaml
servers:
  localhost:
    host: https://localhost
    port: 1337
    socketport: 5000
    username: empireadmin
    password: password123
```
- **suppress-self-cert-warning** - Suppress the http warnings when connecting to an Empire instance that uses a self-signed cert
- **shortcuts** - Shortcuts defined here allow the user to define their own frequently used modules and assign a command to them.
Let's look at 3 distinct examples. All of which can be found in the default [config.yaml](./config.yaml)
```yaml
shortcuts:
  powershell:
    sherlock:
      module: powershell/privesc/sherlock
```
This first example is the simplest example. It adds a `sherlock` command to the Interact menu for Powershell agents. It does not pass any specific parameters.

```yaml
shortcuts:
  powershell:
    keylog:
      module: powershell/collection/keylogger
      params:
        - name: Sleep
          value: 1
```
This next one is slightly more complex in that we are telling the shortcut to set the *Sleep* parameter to 1.
Note that if there are any other parameters for this module that we don't define, it will use whatever the default value is.

```yaml
shortcuts:
  powershell:
    bypassuac:
      module: powershell/privesc/bypassuac_eventvwr
      params:
        - name: Listener
          dynamic: true
```
This third one gets a bit more complex. Instead of providing a `value` to the parameter, it is marked as `dynamic`.
This tells the CLI that it expects the user to send the parameters as part of their command. In other words the user needs to type `bypassuac http1` in order for this to execute.
The parameters are passed in the order they are defined in config.yaml. There are some convenient autocompletes if the field is named `Listener` or `Agent`.

### Usage

#### Main Menu
When first loading Empire-Cli, the user will be dropped into the main menu. The only command available is `connect`.
The "short way" to connect is to load the server into config.yaml and call it like `connect -c localhost`.
The "long way" to connect is to provide the host, port, username, password as parameters like `c

#### Admin Menu

#### Listener Menu

#### Use Listener Menu

#### Stager Menu

#### Use Stager Menu

#### Plugin Menu

#### Use Plugin Menu

#### Agent Menu

#### Interact Menu

#### Shell Menu

#### Credential Menu

#### Use Module Menu
