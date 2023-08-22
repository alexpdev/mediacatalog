install: ## install dependencies
	pip install --upgrade PySide6 pyinstaller

clean: ## clean unused folders
	rm -rfv ./**/__pycache__
	rm -rfv dist
	rm -rfv build
	rm -rfv *.zip
	rm -rfv *.spec

run: ## run file
	python run.py

compile: clean ## compile app
	### pyinstaller --icon ./assets/popcorn.ico --add-data "./assets;./assets"  --name Fuzzys_Media_Manager_dev run.py
	pyinstaller -w --icon ./assets/popcorn.ico --add-data "./assets;./assets"  --name Fuzzys_Media_Manager run.py

push: clean ## push to github
	git add .
	git commit -m "$m"
	git push

setup: compile ## run setup installer bundler
	iscc ./output/mediacatalog_setup.iss

bundle: compile
	7z a Fuzzys_Media_Manager_v0.7.zip mediacatalog assets run.py dist README.md CHANGELOG.md "Movies and TV Shows_V18S3 Demo.xlsm" .gitignore
	7z a Fuzzys_Media_Manager_Source_Code.zip mediacatalog
