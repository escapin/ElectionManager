build: 	devenv references roboto

devenv:
	npm install
	mkdir -p webapp/pure
	cd webapp/pure; wget -N http://yui.yahooapis.com/pure/0.5.0/pure-min.css
	cd webapp/pure; wget -N http://yui.yahooapis.com/pure/0.5.0/grids-responsive-old-ie-min.css
	cd webapp/pure; wget -N http://yui.yahooapis.com/pure/0.5.0/grids-responsive-min.css
	cd webapp/js; wget -N http://code.jquery.com/jquery-1.11.1.min.js
	cd webapp/js; wget -N https://cdn.jsdelivr.net/bluebird/latest/bluebird.min.js
	mkdir -p _data_

references:
	mkdir -p webapp/ref
	cd webapp/ref; wget -N http://infsec.uni-trier.de/people/publications/KuestersMuellerScapinTruderung-CSF-2016.bib; mv KuestersMuellerScapinTruderung-CSF-2016.bib KuestersMuellerScapinTruderung-CSF-2016.bib.txt
	cd webapp/ref; wget -N http://infsec.uni-trier.de/people/publications/KuestersMuellerScapinTruderung-CSF-2016.abstract; mv KuestersMuellerScapinTruderung-CSF-2016.abstract KuestersMuellerScapinTruderung-CSF-2016.abstract.txt
	cd webapp/ref; wget -N http://infsec.uni-trier.de/people/publications/paper/KuestersMuellerScapinTruderung-CSF-2016.pdf

roboto:
	cd webapp/roboto; wget -N https://fonts.gstatic.com/s/roboto/v15/Jzo62I39jc0gQRrbndN6nfesZW2xOQ-xsNqO47m55DA.ttf
	cd webapp/roboto; wget -N https://fonts.gstatic.com/s/roboto/v15/Hgo13k-tfSpn0qi1SFdUfaCWcynf_cDxXwCLxiixG1c.ttf
	cd webapp/roboto; wget -N https://fonts.gstatic.com/s/roboto/v15/zN7GBFwfMP4uA6AR0HCoLQ.ttf
	cd webapp/roboto; wget -N https://fonts.gstatic.com/s/roboto/v15/RxZJdnzeo3R5zSexge8UUaCWcynf_cDxXwCLxiixG1c.ttf
	cd webapp/roboto; wget -N https://fonts.gstatic.com/s/roboto/v15/12mE4jfMSBTmg-81EiS-YS3USBnSvpkopQaUR-2r7iU.ttf
	cd webapp/roboto; wget -N https://fonts.gstatic.com/s/roboto/v15/7m8l7TlFO-S3VkhHuR0at50EAVxt0G0biEntp43Qt6E.ttf
	cd webapp/roboto; wget -N https://fonts.gstatic.com/s/roboto/v15/W4wDsBUluyw0tK3tykhXEfesZW2xOQ-xsNqO47m55DA.ttf
	cd webapp/roboto; wget -N https://fonts.gstatic.com/s/roboto/v15/OLffGBTaF0XFOW1gnuHF0Z0EAVxt0G0biEntp43Qt6E.ttf

clean:	devclean refclean robotoclean

devclean:
	-rm -r node_modules
	-rm -r webapp/pure
	-rm webapp/js/jquery-1.11.1.min.js
	-rm webapp/js/bluebird.min.js
	-rm -r _data_

refclean:
	-rm -r webapp/ref
	
robotoclean:
	-rm webapp/roboto/*.ttf
