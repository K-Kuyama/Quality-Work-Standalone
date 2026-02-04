# 変数定義
APP_NAME := quality-work
DIST_DIR := dist_package
LICENSE_DIR := $(DIST_DIR)/licenses
IGNORE_PKGS := pip setuptools wheel pip-licenses pyinstaller pyinstaller-hooks-contrib backend

env:
	poetry install
	#poetry add pyinstaller
	#poetry add pywin32
	poetry run python manage.py migrate
	poetry run python manage.py loaddata fixture.json

module:
	poetry run pyinstaller --clean quality-work.spec

licenses:
	@echo "Generating license information..."
	@mkdir -p $(LICENSE_DIR)
	# 著作権者リスト（Markdown形式）の作成
	poetry run pip-licenses --format=markdown --with-authors --with-urls --ignore-packages $(IGNORE_PKGS) --output-file $(DIST_DIR)/THIRD_PARTY_LICENSES.md
	# ライセンス全文まとめファイルの作成
	poetry run pip-licenses --format=plain-vertical --with-license-file --no-license-path --ignore-packages $(IGNORE_PKGS) --output-file $(LICENSE_DIR)/LICENSE_ALL.txt
	