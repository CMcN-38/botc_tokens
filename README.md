# Token Tools for Blood on the Clocktower
A simple fan-made utility to help create custom tokens for the game Blood on the Clocktower.

[img]

## Installation
To use these scripts, you will need to have Python 3 installed on your computer. You can download it from the [official website](https://www.python.org/downloads/).

Once you have Python installed, you can install these scripts using `pip`:
```bash
pip install botc_tokens
```
or manually by cloning this repository and running the following command in the root folder:
```bash
pip install .
```

## Usage
The main script is run through its entrypoint `botc_tokens`. You can use the `--help` flag to see the available 
commands and options.
A typical workflow would use the `update` command to download the latest assets from the web, and then the `create` 
command to generate the tokens, followed by a `group` command to organize them into a single printable sheet using a 
json file from the [official script tool](https://script.bloodontheclocktower.com/).

### Updating from the web
If you want to create experimental tokens for your in-person games, you can use the `update` command to download the
current list from the [official wiki] (https://wiki.bloodontheclocktower.com/). This is an incremental update, so it 
will only download assets that are not already present in the local folder. We highly recommend double-checking the
resulting entries, especially the reminder token section. While the utility does its best to guess, it isn't perfect.
If you already know the reminder tokens, you can create a JSON file for the utility to use. See the example folder for
an example of the format.
```bash
botc_tokens update --output-dir /path/to/inputs --reminders /path/to/reminders.json
```

### Creating tokens
Once you have your role info, whether from the `update` command or from your own creation, you can use the `create`
command to generate the tokens. This will create a folder with the role name and a subfolder for each token type.
```bash
botc_tokens create /path/to/inputs /path/to/tokens
```

### Grouping tokens
Once you have created your token images, you can use the `group` command to organize the tokens into a single 
printable sheet. This command requires a JSON file with the role info, which can be obtained from the
[official script tool](https://script.bloodontheclocktower.com/).
```bash
botc_tokens group /path/to/script.json --token-dir /path/to/tokens --output-dir /path/to/printables
```

## And that's it!
You can now print your tokens and use them in your games. Remember, this is a fan-made utility and is not
affiliated with the official game in any way. We do not own the rights to the game, and we do not claim to. We are just
fans who want to make the game more accessible to everyone. Please support the creators by 
[buying the game](https://bloodontheclocktower.com/buy). It is absolutely worth it!