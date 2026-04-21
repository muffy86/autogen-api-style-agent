[app]
title = Sovereign Intelligence OS
package.name = sovereignos
package.domain = org.sovereign
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 2026.5.0

requirements = python3,kivy==2.3.1,requests,urllib3,certifi,charset-normalizer,idna

orientation = all
fullscreen = 0

android.api = 34
android.minapi = 29
android.permissions = INTERNET,SYSTEM_ALERT_WINDOW,FOREGROUND_SERVICE
android.archs = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
