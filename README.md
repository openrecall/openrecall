```
   ____                   _____                _ _ 
  / __ \                 |  __ \              | | |
 | |  | |_ __   ___ _ __ | |__) |___  ___ __ _| | |
 | |  | | '_ \ / _ \ '_ \|  _  // _ \/ __/ _` | | |
 | |__| | |_) |  __/ | | | | \ \  __/ (_| (_| | | |
  \____/| .__/ \___|_| |_|_|  \_\___|\___\__,_|_|_|
        | |                                        
        |_|                                        
```

# Take Control of Your Digital Memory

OpenRecall is a fully open-source, privacy-first alternative to proprietary solutions like Microsoft's Windows Recall or Limitless' Rewind.ai. With OpenRecall, you can easily access your digital history, enhancing your memory and productivity without compromising your privacy.

## What does it do?

OpenRecall captures your digital history through regularly taken snapshots, which are essentially screenshots. The text and images within these screenshots are analyzed and made searchable, allowing you to quickly find specific information by typing relevant keywords into OpenRecall. You can also manually scroll back through your history to revisit past activities.

<p align="center">
  <img src="images/lisa_rewind.webp" alt="Lisa Rewind" width="500">
</p>

## Why Choose OpenRecall?

OpenRecall offers several key advantages over closed-source alternatives:

- **Transparency**: OpenRecall is 100% open-source, allowing you to audit the source code for potential backdoors or privacy-invading features.
- **Cross-platform Support**: OpenRecall works seamlessly on Windows, macOS, and Linux, giving you the freedom to use it on your preferred operating system.
- **Privacy-focused**: (soon to be implemented) Your data is stored locally on your device, and you have the option to encrypt it with a password for added security. No cloud integration is required. 
- **Hardware Compatibility**: OpenRecall is designed to work with a wide range of hardware, unlike proprietary solutions that may require specific certified devices.

<p align="center">
  <a href="https://twitter.com/elonmusk/status/1792690964672450971">
    <img src="images/black_mirror.png" alt="Elon Musk Tweet" width="500">
  </a>
</p>

## Features

- **Time Travel**: Go back in time and revisit your digital activities on Windows, macOS, or Linux.
- **Local-first AI**: OpenRecall leverages local AI processing to ensure your data remains private and secure.
- **Encrypted Storage**: (soon to be implemented) Optionally encrypt your local data with a password to protect against unauthorized access, even if your device is lost or stolen.
- **Pause Functionality**: Pause OpenRecall indefinitely or for a specified duration (e.g., 30 minutes) to maintain privacy when needed.
- **Exclude apps**: Exclude apps that you do not want to record for privacy

## Comparison

| Feature          | OpenRecall                    | Windows Recall                                  | Rewind.ai                              |
|------------------|-------------------------------|--------------------------------------------------|----------------------------------------|
| Transparency     | Open-source                   | Closed-source                                    | Closed-source                          |
| Supported Hardware | All                         | Copilot+ certified Windows hardware              | M1/M2 Apple Silicon                    |
| OS Support       | Windows, macOS, Linux         | Windows                                          | macOS                                  |
| Privacy          | On-device, self-hosted        | Microsoft's privacy policy applies               | Connected to ChatGPT                   |

## Roadmap

We have exciting plans for OpenRecall's future, including:

- Visual search capabilities
- Audio transcription for enhanced searchability

## Get Started

<<<<<<< HEAD:README.md
### Prerequisites
- Python 3.11
- MacOSX/Windows/Linux

To install:
```
pip install git+https://github.com/openrecall/openrecall.git
```
To run:
```
python3 -m openrecall.app
```
Open your browser to:
[http://localhost:8082](http://localhost:8082) to access OpenRecall.
=======
To start using OpenRecall, simply pip install and run

```
pip install openrecall
```
>>>>>>> 2a1f12be9a8cf2aab83942384d7107acb829d3a9:readme.md

## Contribute

As an open-source project, we welcome contributions from the community. If you'd like to help improve OpenRecall, please submit a pull request or open an issue on our GitHub repository.

## License

OpenRecall is released under the [AGPLv3](https://opensource.org/licenses/AGPL-3.0), ensuring that it remains open and accessible to everyone.