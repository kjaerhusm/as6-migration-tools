# as6-migration-tools

**Open-source tools for analyzing and migrating B&R Automation Studio 4 (AS4) projects to Automation Studio 6 (AS6).**  
Detects obsolete libraries, unsupported hardware, deprecated functions - and includes helper scripts for automatic code conversion.

> ⚠️ **Disclaimer:** This project is **unofficial** and not provided or endorsed by B&R Industrial Automation.  
> It is offered as an open-source tool, with no warranty or guarantees.  
> Use at your own risk - contributions and improvements are very welcome!

---

## Features

- Analyze AS4 project structure and content
- Detect obsolete and deprecated libraries
- Identify unsupported hardware components
- Find deprecated function blocks and functions
- Suggest library upgrades and replacements
- Check project and hardware file compatibility with AS6
- Includes helper scripts for code migration and conversion  
- Easily extendable to support more patterns and conversions

---

## Installation

- ✅ **Recommended:** Download the latest release from [GitHub Releases](https://github.com/br-automation-community/as6-migration-tools/releases/tag/latest)  
  Unzip and run `as6-migration-tools.exe`.

- 🐍 **Alternative (Python source):**  
  Run `pip install -r requirements.txt`

## Usage

Launch `gui_launcher.py` to open the GUI.  
Choose the target script, browse to your AS4 project, and click **Run**.

![Example Analysis Output](docs/gui1.png)

Run any of the scripts from the command line:

```bash
usage: python as4_to_as6_analyzer.py project_path [options]

Scans Automation Studio project for transition from AS4 to AS6

positional arguments:
  project_path   Automation Studio 4.x path containing *.apj file

options:
  -h,		--help			Show this help message and exit
  -v,		--verbose		Outputs verbose information
  -no-file,	--no-file		Skip creating the analysis file in the AS folder

```

Example:

Run the main script to analyze an Automation Studio 4.12.x project:

```bash
python as4_to_as6_analyzer.py "C:\path\to\AutomationStudio4Project"
```

> 💡 **Tip:** If you're using WSL, convert Windows paths like this:  
> `C:\Projects\MyProject` → `/mnt/c/Projects/MyProject`


---

## Example Output

The `as4_to_as6_analyzer.py` script generates a detailed migration report (saved as `as4_to_as6_analyzer_result.txt` in the project folder).

The report shows which obsolete libraries, hardware components, and function blocks were found - along with suggested actions.

Example (partial output):

![Example Analysis Output](docs/example_output.png)

---

## Included Scripts

| Script                           | Purpose                                                |
|----------------------------------|--------------------------------------------------------|
| `gui_launcher.py`                | GUI for running the scripts                            |
| `as4_to_as6_analyzer.py`         | Main analysis and migration report generator           |
| `helpers/asmath_to_asbrmath.py`  | Replaces deprecated AsMath functions                   |
| `helpers/asstring_to_asbrstr.py` | Replaces deprecated AsString functions                 |
| `helpers/asopcua_update.py`      | Updates OPC UA client code for AR 6 compatibility      |
| `helpers/create_mapp_folders.py` | Creates the newer folders for the mapp components      |
| `helpers/mappmotion_update.py`   | Updates mappMotion code for mappMotion 6 compatibility |

Additional helper scripts may be added in future versions - pull requests welcome.

### Calling a helper script directly

Due to the structure of the project, calling `python helpers/<anyscript>.py` will result in an error.
To prevent this, either use the GUI or change the call to `python -m helpers.<anyscript>` (omit the `.py` extension)

---

## Requirements

- Python 3.12 (tested)
- Designed for Automation Studio 4.12 projects
- Generates reports to assist in migration to Automation Studio 6.x

---

## Limitations

- This tool does not perform full automatic migration of projects.
- It provides analysis and recommendations to assist developers during migration.
- Helper scripts make best-effort changes based on known patterns, but may not cover all edge cases.
- Manual review and validation is always required after running the tool.

---

## Contributing

- Found an issue? Please open a GitHub issue.
- Have ideas or improvements?  
  Fork the repo and submit a pull request - contributions are very welcome!
  - Please run the [black](https://black.readthedocs.io/en/stable/) formatter prior to committing any changes to ensure a consistent style. \
    Hint: PyCharm allows to do so automatically via Settings->Tools->Black

---

## License

MIT License - free to use for personal or commercial purposes.

---

This project is built by and for the B&R developer community.  
It helps analyze existing AS4 projects, detect potential upgrade issues, and simplify the transition to AS6.

We hope it saves you time and gives you a head start - feedback and pull requests are always welcome 🚀
