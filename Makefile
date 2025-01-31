.PHONY: check install build clean run dmg update-homebrew

check:
	@echo "Checking system requirements..."
	@command -v colima >/dev/null 2>&1 || { echo >&2 "Colima is not installed. Install with brew install colima. Aborting."; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo >&2 "Docker is not installed. Install with brew install docker. Aborting."; exit 1; }
	@command -v poetry >/dev/null 2>&1 || { echo >&2 "Poetry is not installed. Install with brew install poetry. Aborting."; exit 1; }
	@command -v create-dmg >/dev/null 2>&1 || { echo >&2 "create-dmg is not installed. Install with brew install create-dmg. Aborting."; exit 1; }

install: check
	@echo "Installing dependencies with Poetry..."
	@poetry install

build: install
	@echo "Building application..."
	@poetry run python setup.py py2app

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build dist *.egg-info
	@find . -type d -name "__pycache__" -exec rm -r {} +

run: clean install
	@echo "Running Colama..."
	@poetry run python -m colama.main

dmg: build
	@echo "Creating DMG file..."
	@create-dmg \
		--volname "Co-lama Installer" \
		--volicon "resources/lama.icns" \
		--window-pos 200 120 \
		--window-size 800 400 \
		--icon-size 100 \
		--icon "Co-lama.app" 200 190 \
		--hide-extension "Co-lama.app" \
		--app-drop-link 600 185 \
		"dist/Co-lama-Installer.dmg" \
		"dist/Co-lama.app"

update-homebrew:
	@echo "Updating Homebrew formula..."
	@git tag -d v0.1.0 || true
	@git push --delete origin v0.1.0 || true
	@git tag v0.1.0
	@git push origin v0.1.0
	@echo "Getting new SHA256..."
	@curl -sL https://github.com/lvonsydow/co-lama/archive/refs/tags/v0.1.0.tar.gz | shasum -a 256 | cut -d ' ' -f 1 > /tmp/co-lama-sha
	@cd ../homebrew-co-lama && \
		sed -i '' "s/sha256 \".*\"/sha256 \"$$(cat /tmp/co-lama-sha)\"/" co-lama.rb && \
		git add co-lama.rb && \
		git commit -m "Update SHA256 for co-lama archive" && \
		git push
	@rm /tmp/co-lama-sha
	@echo "Done! Now run: brew uninstall co-lama && brew untap lvonsydow/co-lama && brew tap lvonsydow/co-lama && brew install co-lama"

.DEFAULT_GOAL := build
