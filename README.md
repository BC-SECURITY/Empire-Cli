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
The "long way" to connect is to provide the host, port, username, password as parameters... todo.

#### Admin Menu
The admin menu is an administrative menu which gives the team server admin the options to manage users and server options.
The admin menu can be accessed by typing `admin` into the console. Once on this page, the admin can add/remove users from
the team server and can modify the types of obfuscation the agents will use.

Regular users will not be able to modify settings, but will have access to accessing the notes features. Notes allow users
to record information within their session and have them stored on the server. They can access their notes from any session
once they are sent to the server.

#### Listener Menu

#### Use Listener Menu

#### Stager Menu

#### Use Stager Menu

#### Plugin Menu
Plugins are an extension of Empire that allow for custom scripts to be loaded. This allows anyone to easily build or 
add community projects to extend Empire functionality. Plugins can be accessed from the Empire CLI as long 
as the plugin follows the [template example](./plugins/example.py). A list of Empire Plugins is located 
[here](plugins/PLUGINS.md).

The Plugins Menu, is displays all of the currently loaded plugins available to the user. You will then need to call 
`useplugin` to be able to access the functionality of a plugin.

#### Use Plugin Menu
Interacting with plugins will look very similliar to you interact with modules. You will type `useplugin <plugi_name>` 
to load a specific plugin. Next, you can edit the options using the `set` command. Once you are done, `execute` will 
launch the plugin's functionality.

#### Agent Menu

#### Interact Menu

#### Shell Menu
The interactive shell menu opens a shell-like environment for an agent that gives the look/feel of a real shell session. 
This window includes the current working directory being displayed to the user. All commands will be sent to the agent 
and returned to the interactive shell window. To run the interactive shell, just type `shell` inside of any agent and 
to exit the shell session, type `exit` to return to the agent.

#### Credential Menu

#### Use Module Menu

#### Chat Menu