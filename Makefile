dist: 
	rm -f *.zip
	rm -f *.tar.gz
	find . -name '*~' -exec rm -f {} \;
	rm -f *.pyc
	zip -r optimus_prototype.zip .
	cd ..
	cd .. && tar zcvf optimus_prototype.tar.gz optimus/*.py optimus/simulations optimus/doc
	mv ../optimus_prototype.tar.gz .

