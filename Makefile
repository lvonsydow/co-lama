phony: hasColima hasDocker hasPip installDependencies buildApp installApp

hasColima:
	@echo "Checking if Colima is installed..."
	@command -v colima >/dev/null 2>&1 || { echo >&2 "Colima is not installed. Install with brew `brew install colima`  Aborting."; exit 1; }
hasDocker:
	@echo "Checking if Docker is installed..."
	@command -v docker >/dev/null 2>&1 || { echo >&2 "Docker is not installed. Install with brew `brew install docker`  Aborting."; exit 1; }
hasPip:
	@echo "Checking if pip is installed..."
	@command -v pip >/dev/null 2>&1 || { echo >&2 "pip is not installed. Install with `curl https://bootstrap.pypa.io/get-pip.py | python3`  Aborting."; exit 1; }

installDependencies: hasColima hasDocker hasPip
	@echo "Installing dependencies..."
	@pip install --use-pep517 -r requirements.txt

build: installDependencies
	@echo "Building app..."
	@python3 setup.py py2app

install: build
	@echo "Installing app..."
	@cp -r dist/Co-lama.app /Applications
	@rm -rf build dist
	@echo "Done! 🎉"
