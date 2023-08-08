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
	pyinstaller -F -w --icon ./assets/popcorn.ico --add-data "./assets;./assets"  --name Fuzzys_Media_Manager run.py

push: clean ## push to github
	git add .
	git commit -m "$m"
	git push
