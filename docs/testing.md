# Testing

A set of tests is provided in the tests directory. To setup testing with VSCode, press 
* Ctrl + Shift + P, 
* Python: Configure Tests
* Select "PyTest" as testenvironment
* Select tests as test directory
VS Code should show all tests in the test tab

To run the tests from command line execute

```bash
python3 -m pytest
```

# Flask Server debugging in vscode
This is an example launch.json file in the .vscode directory. You can start the webserver without taking screenshots and debug the we app.

```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: Flask",
            "type": "debugpy",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "openrecall\\app.py",
                "FLASK_DEBUG": "1"
            },
            "args": [
                "run",
                "--no-debugger",
                "--no-reload"
            ],
            "jinja": true,
            "autoStartBrowser": false
        }
    ]
}
```