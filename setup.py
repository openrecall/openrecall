import io
import platform

from setuptools import find_packages, setup

# Read the README.md file
with io.open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

install_requires = [
    "Flask==3.0.3",
    "numpy==1.26.4",
    "mss==9.0.1",
    "sentence-transformers==3.0.0",
    "torch==2.2.0",
    "torchvision==0.17.0",
    "shapely==2.0.4",
    "h5py==3.11.0",
    "rapidfuzz==3.9.3",
    "Pillow==10.3.0",
]

# Define OS-specific dependencies
extras_require = {
    "windows": ["pywin32", "psutil"],
    "macos": ["pyobjc==10.3"],
    "linux": [],
    "python-doctr": [
        "python-doctr @ git+https://github.com/koenvaneijk/doctr.git@af711bc04eb8876a7189923fb51ec44481ee18cd"
    ],
}

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

install_requires.extend(extras_require.get("python-doctr", []))

setup(
    name="OpenRecall",
    version="0.8",
    packages=find_packages(),
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type="text/markdown",
    extras_require=extras_require,
)
