[app]
title = Shooter Game
package.name = shootergame
package.domain = org.shooter
source.dir = .
source.include_exts = py,png,jpg,jpeg,csv,wav,mp3,ogg
source.exclude_dirs = .venv,dist,build,__pycache__
version = 1.0
requirements = python3,pygame
orientation = landscape
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.api = 33
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.permissions =
android.accept_sdk_license = True
