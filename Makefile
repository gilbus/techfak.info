KEY_FILE=
MACHINE=
USER=
SSH=$(USER)@$(MACHINE)
PREFIX?=
DEMO_ENTRIES_FILE?=share/dummy_data.json

local_install:
	cp -r lib/techfak.info $(PREFIX)/lib/
	cp bin/status $(PREFIX)/bin/
	find $(PREFIX)/lib/techfak.info/techfak_info -type f -exec chmod 644 {} \;
	find $(PREFIX)/lib/techfak.info -type f -name 'techfak_info-*' -exec chmod 755 {} \;
	chmod 755 $(PREFIX)/bin/status


remote_install:
	@echo "Installing all scripts to remote machine using /usr/local as PREFIX"
	ssh-add -t 1m $(KEY_FILE)
	scp -r lib/techfak.info $(SSH):/usr/local/lib/
	scp bin/status-local $(SSH):/usr/local/bin/status
	ssh $(SSH) "find /usr/local/lib/techfak.info/techfak_info -type f -exec chmod 644 {} \;"
	ssh $(SSH) "find /usr/local/lib/techfak.info -type f -exec chmod 755 {} \;"
	ssh $(SSH) "chmod 755 /usr/local/bin/status"
	scp etc/techfak_info.conf $(SSH):/usr/local/etc/
	ssh $(SSH) 'mkdir -p /usr/local/share/techfak.info'
	scp -r share/templates $(SSH):/usr/local/share/techfak.info/
	rsync -azv -e ssh --delete resources/ $(SSH):/srv/www/status/resources
	ssh $(SSH) 'chown status:users -R /srv/www/status'

clear-pyc:
	find -name '*.pyc' -exec rm --force {} \;
	find -type d -name '*.mypy_cache' -exec rm --recursive --force {} \;

clear-build:
	rm -rf build/*

demo:
	@echo "Specify the file with entries via DEMO_ENTRIES_FILE ($(DEMO_ENTRIES_FILE))"
	mkdir -p build
	lib/techfak.info/techfak_info-build -l $(DEMO_ENTRIES_FILE) -p infopage -o build/infopage.html
	lib/techfak.info/techfak_info-build -l $(DEMO_ENTRIES_FILE) -p infopage -o build/infopage_empty.html --hide-all
	lib/techfak.info/techfak_info-build -l $(DEMO_ENTRIES_FILE) -p monitor -o build/monitor.html
	lib/techfak.info/techfak_info-build -l $(DEMO_ENTRIES_FILE) -p monitor -o build/monitor_empty.html --hide-all
	@echo "Now open http://localhost:8000/build"
	#python3 -m http.server


