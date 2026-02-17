fname = frontend
fileexists = $(cd ../backend && (shell ls | grep ${fname}))

# 変数
DIST_DIR := dist_package
#JS_LICENSE_FILE := $(DIST_DIR)/JS_LICENSES_ALL.txt
EXCLUED_LIST := frontend

env:
	#npx create-react-app .
	npm install

module:
	npm run build
	rm -rf ../backend/frontend
	cp -r build ../backend/frontend
	cp build/index.html ../backend/templates/

license-js:
	@echo "Extracting and formatting JS licenses to match pip-licenses style..."
	@mkdir -p $(DIST_DIR)
	# 一旦JSONですべて抽出
	(npx license-checker --production --customPath customFormat.json --json --out $(DIST_DIR)/tmp_raw.json && sleep 1)
	# 各パッケージの情報を区切り線付きでテキスト化する例
	jq -r '.[] | select(.name != "frontend")| "Name: \(.name)\nVersion: \(.version)\nLicense: \(.licenses)\n\n\(.licenseText)\n\n--------------------------------\n"' $(DIST_DIR)/tmp_raw.json > $(DIST_DIR)/JS_LICENSES.txt
	rm $(DIST_DIR)/tmp_raw.json