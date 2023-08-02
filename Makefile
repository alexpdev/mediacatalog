install: ## install dependencies
	pip install --upgrade PySide6 pyinstaller
	

clean: ## clean unused folders
	rm -rfv ./**/__pycache__
	rm -rfv dist
	rm -rfv build
	
run: ## run file
	python run.py
	
compile: ## compile app
	pyinstaller -F -w --name mediacatalog run.py
