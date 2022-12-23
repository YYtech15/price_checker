import secrets
from waitress import serve
from run import app,Crawler

app.config['SECRET_KEY'] = secrets.token_hex()

port = 9999

crawler = Crawler(60)
if __name__ == '__main__':
	crawler.start()
	print("Backend server is running on port %d" % port)
	serve(app, host="0.0.0.0", port=port)
