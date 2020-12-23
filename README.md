**This code is in a beta state. There may be bugs and major changes before a full release.
Please provide feedback and bugs in the [issues](https://github.com/BC-SECURITY/Empire-Cli/issues) or in our Discord**

Empire-Cli
=============================
The new Empire CLI is a python command-line application written using [python-prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit).
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
This tells Empire-Cli to use the connection info for the server named localhost from the yaml. In addition, if autoconnect is set to `True`, the Cli will automatically connect to that server when starting up.
```yaml
servers:
  localhost:
    host: https://localhost
    port: 1337
    socketport: 5000
    username: empireadmin
    password: password123
    autoconnect: True
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

```yaml
shortcuts:
  powershell:
    whoami:
      shell: whoami
```
The last one is much more simple. Instead of running a module, we run a shell command.

- **resource-file** - A resource file as simply a text file with a list of commands to run in order.
An example txt is shown below
```yaml
resource-file: commands.txt

# commands.txt
listeners
uselistener http
set Port 999
execute
```

### Usage

#### Main Menu
When first loading Empire-Cli, the user will be dropped into the main menu. The only command available is `connect`.
The "short way" to connect is to load the server into config.yaml and call it like `connect -c localhost`.
The "long way" to connect is to provide the host, port, username, password as parameters... todo.

![empirecli_splashpage](https://user-images.githubusercontent.com/20302208/100279434-603a7b80-2f1b-11eb-880e-4450ac5d2e62.jpg)

#### Admin Menu
The admin menu is an administrative menu which gives the team server admin the options to manage users and server options.
The admin menu can be accessed by typing `admin` into the console. Once on this page, the admin can add/remove users from
the team server and can modify the types of obfuscation the agents will use.

Regular users will not be able to modify settings, but will have access to accessing the notes features. Notes allow users
to record information within their session and have them stored on the server. They can access their notes from any session
once they are sent to the server.

![empirecli_admin](https://user-images.githubusercontent.com/20302208/100279600-b5768d00-2f1b-11eb-8096-cebda7597f1b.jpg)

#### Listener Menu
The listener menu gives an overview list of all active listeners. A listener can be killed by typing the command `kill <listener_name>`.

#### Use Listener Menu
The listener commands include:

- View the listener info: `info`
- Set listener settings: `set <listener_option>`
- Execute/generate the current listener: `execute`

![listeners](https://user-images.githubusercontent.com/20302208/100279698-e951b280-2f1b-11eb-947a-b5f162f04b17.jpg)

#### Use Stager Menu
Empire implements various stagers in a modular format in ./lib/stagers/*. These include DLLs, macros, one-liners, 
and more. To use a stager type `usestager <stager_name>` or tap tab-complete to select an available stager. The stager 
commands include:

- View the stager info: `info`
- Set stager settings: `set <stager_option>`
- Execute/generate the current stager: `execute`

![usestager](https://user-images.githubusercontent.com/20302208/100279741-fbcbec00-2f1b-11eb-9a3a-bac5e9a9716c.jpg)

#### Plugin Menu
Plugins are an extension of Empire that allow for custom scripts to be loaded. This allows anyone to easily build or 
add community projects to extend Empire functionality. Plugins can be accessed from the Empire CLI as long 
as the plugin follows the [template example](./plugins/example.py). A list of Empire Plugins is located 
[here](plugins/PLUGINS.md).

The Plugins Menu, is displays all of the currently loaded plugins available to the user. You will then need to call 
`useplugin` to be able to access the functionality of a plugin.

![empirecli_plugins](https://user-images.githubusercontent.com/20302208/100279849-228a2280-2f1c-11eb-989e-df8812cefdb8.jpg)

#### Use Plugin Menu
Interacting with plugins will look very similar to you interact with modules. You will type `useplugin <plugi_name>` 
to load a specific plugin. Next, you can edit the options using the `set` command. Once you are done, `execute` will 
launch the plugin's functionality.

![useplugin](https://user-images.githubusercontent.com/20302208/100279824-17cf8d80-2f1c-11eb-963e-b0940bdd4107.jpg)

#### Agent Menu
Agents are Empire's implants that are used to interact and assign tasks and collect information. A list of active agents
is displayed when entering this page and highlghts active agents green and stale agents red. From this menu, you can 
kill, remove, rename, and clear an agent using their respective commands.

![agents](https://user-images.githubusercontent.com/20302208/100279870-2ddd4e00-2f1c-11eb-9431-c1ba796af721.jpg)

#### Interact Menu
Interacting with an agent is how operators manage their implants. Usemodule is accessible from inside an agent and will prepopulate the agent in the options. The interactive shell menu can be accessed by typing `shell`, or you can run a command directly by `shell <command>`. Other options are downloading and uploading files, managing agent comms, and agent configurations.

![interact](https://user-images.githubusercontent.com/20302208/100279892-33d32f00-2f1c-11eb-9046-1822c222e5e7.jpg)

#### Shell Menu
The interactive shell menu opens a shell-like environment for an agent that gives the look/feel of a real shell session. 
This window includes the current working directory being displayed to the user. All commands will be sent to the agent 
and returned to the interactive shell window. To run the interactive shell, just type `shell` inside of any agent and 
to exit the shell session, type `exit` to return to the agent.

![interactiveshell](https://user-images.githubusercontent.com/20302208/100279910-3a61a680-2f1c-11eb-9215-0b0e2ad17e2a.jpg)

#### Credential Menu
Empire will attempt to parse standard Mimikatz outputs and keep them in an internal credential store. Credentials can 
be viewed from anywhere with the `credentials` command. The credential store can effectively operate as a golden and 
silver ticket catalog generating the appropriate ticket on demand, storing passwords, and hashes. Credentials can be 
added to the database by typing `add <domain> <username> <password>`.

![credentials](https://user-images.githubusercontent.com/20302208/100279997-58c7a200-2f1c-11eb-9230-9becfb48bf9a.jpg)

#### Use Module Menu
Modules are containers for embedding programs into PowerShell and Python scripts. 
This includes the following module categories:
- Code Execution
- Collection
- Credentials
- Lateral Movements
- Management
- Persistence
- Privilege Escalation
- Situational Awareness
- Trollsploit

![usemodule](https://user-images.githubusercontent.com/20302208/100280026-611fdd00-2f1c-11eb-8a9f-52df3540e112.jpg)

#### Chat Menu
The chat menu interacts with the chat server in Empire. This allows users to drop in and out of the chatroom by typing
`chat`. The 20 most recent messages will be displayed when you login to the room. When you are ready to return to your 
previous task,type `back` and you return to your previous menu.

![empirecli_chat](https://user-images.githubusercontent.com/20302208/100280043-6846eb00-2f1c-11eb-9e61-4e2c54ca180e.jpg)

