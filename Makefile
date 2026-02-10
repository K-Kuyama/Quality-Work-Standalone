ENV_TARGET = env_mac
ifeq ($(OS),Windows_NT)
    MAKE := make
    ENV_TARGET := env_win
endif

env:
	$(MAKE) $(ENV_TARGET)

env_mac:
	$(MAKE) env -C backend
	$(MAKE) env -C frontend

env_win:
	cp backend/pyproject-windows.toml backend/pyproject.toml
	cp backend/poetry-win.lock backend/poetry.lock
	cp backend/quality-work-windows.file backend/quality-work.spec
	cp backend/media/audio_settings-windows.json backend/media/audio_settings.json
	$(MAKE) env -C backend
	$(MAKE) env -C frontend

module:
	$(MAKE) module -C frontend
	$(MAKE) module -C backend

license-txt:
	$(MAKE) license-js -C frontend
	$(MAKE) license-py -C backend
	cp frontend/dist_package/*.txt Licenses/
	cp backend/dist_package/licenses/*.txt Licenses/
	