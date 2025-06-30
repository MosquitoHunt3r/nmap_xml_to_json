## Nmap XML output to JSON
Just a simple python3 script that takes in nmap output in xml format and transforms it into json format.

## Why?
Well 'grepable' output is great but it lacks a lot of information, and json is just perfect for parsing and reusability. While there is already built-in functionality in nmap that allows you to output to json using `-oJ`, it requires to compile nmap binary with the `--with-json` flag, which we don't always have the time for. Same thing goes for this other super awesome script by `@vdjagilev` written in go, it requires steps that we don't always want.

Python comes pre-installed in most distros, and we just want some quick and easy json output!

Since I didn't find any script of this sort online ( that gives GOOD results and/or is written in PYTHON! ), I created my own and decided to share it with the world.

## HOW TO
`-f` flag is to specify the xml file location. If this is left empty it reads from STDIN\
`-o` flag is to specify the file to output to, such as: `-o nmap.json`\
`--no-print` flag is to not print to screen, default is to print
