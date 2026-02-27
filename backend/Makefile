# 変数定義
APP_NAME := quality-work
DIST_DIR := dist_package
LICENSE_DIR := $(DIST_DIR)/licenses
IGNORE_PKGS := pip setuptools wheel pip-licenses pyinstaller pyinstaller-hooks-contrib backend
PYTHON_PATH := $(shell which python || which python3.12 2>/dev/null || which python3 2>/dev/null )
PYTHON_MODULE ?= $(shell cygpath -w $(PYTHON_PATH))
POETRY ?= poetry

env:
	$(POETRY) env use $(PYTHON_MODULE)
	$(POETRY) install
	#poetry add pyinstaller
	#poetry add pywin32
	$(POETRY) run python manage.py migrate
	$(POETRY) run python manage.py loaddata fixture.json

module:
	$(POETRY) run pyinstaller --clean quality-work.spec

license-py:
	@echo "Generating license information..."
	@mkdir -p $(LICENSE_DIR)
	# 著作権者リスト（Markdown形式）の作成
	$(POETRY) run pip-licenses --format=markdown --with-authors --with-urls --ignore-packages $(IGNORE_PKGS) --output-file $(DIST_DIR)/THIRD_PARTY_LICENSES.md
	# ライセンス全文まとめファイルの作成
	$(POETRY) run pip-licenses --format=plain-vertical --with-license-file --no-license-path --ignore-packages $(IGNORE_PKGS) --output-file $(LICENSE_DIR)/PY_LICENSES.txt
	