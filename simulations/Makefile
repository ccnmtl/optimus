dist:
	rm -f *.zip
	rm -f *.tar.gz
	find . -name '*~' -exec rm -f {} \;
	rm -f *.pyc
	zip -r optimus_simulations.zip .
	cd .. && tar zvcf optimus_simulations.tar.gz optimus_simulations/
	mv ../optimus_simulations.tar.gz .
