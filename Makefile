help:
	echo "list command: cleanup, preparedocker, coverage, dockertest, unittest, integrationtest, run"
cleanup:
	rm -f docker_test/main/main.py
	rm -rf docker_test/main/mocks/
	rm -f docker_test/main/mocks_folder
	rm -f docker_test/main/requirements.txt
	rm -f docker_test/main/sample_use.py
	rm -rf SAMPLE_USE_*
	rm -f nohup.out

preparedocker:
	cp main.py docker_test/main/
	cp sample_use.py docker_test/main/
	cp requirements.txt docker_test/main/
	cp mocks_folder docker_test/main/
	cp -r mocks docker_test/main/

dockertest: preparedocker
	docker-compose -f docker_test/docker-compose.yml build
	docker-compose -f docker_test/docker-compose.yml up

coverage:
	coverage run -m unittest discover -s unit_test
	coverage html

unittest:
	python -m unittest discover -s unit_test

integrationtest:
	nohup python main.py 30000 &
	sleep 3
	export PORT=30000 python sample_use.py
	rm -f nohup.out
	echo mocks > mocks_folder
	echo lastLine

run:
	python main.py
