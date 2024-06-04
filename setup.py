import io
import platform

from setuptools import find_packages, setup

# Read the README.md file
with io.open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Read the requirements from requirements.txt
with open("requirements.txt", "r") as f:
    install_requires = [line.strip() for line in f.readlines()]

# Define OS-specific dependencies
extras_require = {"windows": ["pywin32"], "macos": ["pyobjc"], "linux": []}

# Determine the current OS
current_os = platform.system().lower()
if current_os.startswith("win"):
    current_os = "windows"
elif current_os == "darwin":
    current_os = "macos"
elif current_os == "linux":
    current_os = "linux"
else:
    current_os = None

# Include the OS-specific dependencies if the current OS is recognized
if current_os and current_os in extras_require:
    install_requires.extend(extras_require[current_os])

setup(
    name="OpenRecall",
    version="0.1",
    packages=find_packages(),
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type="text/markdown",
    extras_require=extras_require,
)
