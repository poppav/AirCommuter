SOUND FILES DIRECTORY
=====================

Place your custom sound files in this directory to replace the default Windows system sounds.

Supported formats: MP3, WAV, OGG

File naming convention:
- click.mp3 (or click.wav) - Button click sounds
- success.mp3 - Success/positive actions
- error.mp3 - Error/warning sounds
- achievement.mp3 - Achievement unlocked
- notification.mp3 - General notifications

The game will automatically use these files if they exist, otherwise it will fall back to Windows system sounds.

To use MP3 files, you'll need to install one of these libraries:
- pygame: pip install pygame
- playsound: pip install playsound

WAV files work with the built-in winsound module (Windows only).
