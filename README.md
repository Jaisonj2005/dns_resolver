# Bulk DNS Resolver 🌍

A Python-based Open-Source Intelligence (OSINT) and Threat Hunting tool designed for SOC Analysts to rapidly validate large lists of domains and subdomains extracted from malware analysis or phishing investigations.

**Features:**
* Utilizes Python's native `socket` library to execute extremely fast DNS A-Record lookups.
* Automatically sanitizes raw input to strip URL schemes (`http://`, `https://`) and file paths, isolating the raw domain.
* Accurately flags `NXDOMAIN` (Non-Existent Domain) responses to identify dead Command & Control (C2) infrastructure.
* Features a split-pane Tkinter GUI with multi-threading to prevent UI lockups during bulk resolution of hundreds of targets.

*Built as Day 21 of a 30-Day Network Engineering & Security portfolio streak.*
