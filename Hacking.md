# Tips for local development

## Virtualenv and Packages

To simulate the exact package versions as on the status machine use a python3
virtualenv.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Custom config

If a valid `techfak_info.conf` file is found in the **current** directory it is parsed
**after** the regular one, allowing one to overwrite custom values.

Example:
```ini
[DEFAULT]
html_dir = build
; testing data inside the repo
data_path = share/dummy_data.json
; custom path to the template files inside the repo
template_dir = share/templates
; rename from index.html to avoid autoload of it when simply opening the build
; folder inside a browser
info_page = ${html_dir}/infopage.html

; use a local smtp server for testing
[mail]
smtp_port = 8025
smtp_server = localhost

; vim: ft=ini
```

### Local tests

Do not call any of the `status` scripts directly since they are production ready and
will connect you with the status-machine. Call the individual scripts inside
`lib/techfak.info` (TODO: should be `libexec`) to test their function. Make sure that
you have a custom config as written to not send actual mails.

If you're a tmux user: There is a `tmuxp` layout file which gives you a nice shell
setup.

## Local mails

Use a local `smtp` server to quickly view send mails without spamming your regular
inbox, e.g. `python -m smtpd -n -c DebuggingServer localhost:8025`.  Use the function
`unb() {echo "${@}" | sed "s/b'//g" | sed "s/'//g" | sed "s/\n//g" | base64 -d -}` in
case of `base64`-encoded content. `unb <body_of_message>`

## Local preview

`python -m http.server` starts a local HTTP-server which is perfectly suitable for
previewing generated webpages, also used by `make demo`.

## Import from regular python shell

Export `PYTHONPATH=lib/techfak.info` to be able to directly import the
`techfak_info`-lib inside a regular python shell.
