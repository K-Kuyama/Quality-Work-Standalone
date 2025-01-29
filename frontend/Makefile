fname = frontend
fileexists = $(cd ../backend && (shell ls | grep ${fname}))


env:
	#npx create-react-app .
	npm install

module:
	npm run build
	rm -rf ../backend/frontend
	cp -r build ../backend/frontend
	cp build/index.html ../backend/templates/

