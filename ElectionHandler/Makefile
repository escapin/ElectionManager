build: 	devenv references

devenv:
	npm install
	cp ../node_modules/cryptofunc/index.js webapp/js/cryptofunc.js
	mkdir -p webapp/pure
	cd webapp/pure; wget -N http://yui.yahooapis.com/pure/0.5.0/pure-min.css
	cd webapp/pure; wget -N http://yui.yahooapis.com/pure/0.5.0/grids-responsive-old-ie-min.css
	cd webapp/pure; wget -N http://yui.yahooapis.com/pure/0.5.0/grids-responsive-min.css
	cd webapp/js; wget -N http://code.jquery.com/jquery-1.11.1.min.js
	cd webapp/js; wget -N https://cdn.jsdelivr.net/bluebird/latest/bluebird.min.js
	mkdir -p _data_

references:
	mkdir -p webapp/ref
	cd webapp/ref; wget -N http://infsec.uni-trier.de/people/publications/KuestersMuellerScapinTruderung-TR-sElect-2016.bib
	cd webapp/ref; wget -N http://infsec.uni-trier.de/people/publications/KuestersMuellerScapinTruderung-TR-sElect-2016.abstract
	cd webapp/ref; wget -N  http://infsec.uni-trier.de/people/publications/paper/KuestersMuellerScapinTruderung-TR-sElect-2016.pdf

clean:	devclean refclean

devclean:
	-rm -r node_modules
	-rm -r webapp/pure
	-rm webapp/js/jquery-1.11.1.min.js
	-rm webapp/js/bluebird.min.js
	-rm -r _data_

refclean:
	-rm -r webapp/ref
