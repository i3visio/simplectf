SimpleCTF: A Terminal Compliant CTF Platform
============================================

Description
-----------

Just a lightweight terminal compliant CTF platform with which users can interact
using curl. Nothing serious.

Because you don't need a web browser to hack like a *pro*! :)

Installation
------------

To install the project you should clone the Github repository:
```
git clone https://github.com/i3visio/simplectf
cd simplectf
```

Then, install the dependencies for the current user:
```
pip install -r requirements --user
```

Change directory to the `simplectf` folder and run the server with the rules
file. There is one as an example in the `config` folder.
```
python ctf_server.py --rules config/sample-ctf.cfg
```

By default, the server is available in `localhost:5000`. You can check it with:
```
curl localhost:5000
```

If you want to make the server fully available to anyone connecting to the
machine (we hope you understand what you are doing!), launch it setting the
`--host` option:
```
python ctf_server.py --rules config/sample-ctf.cfg --host 0.0.0.0
```

Authors
-------

Yaiza Rubio (@yrubiosec) and Félix Brezo (@febrezo).
