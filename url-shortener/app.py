from flask import Flask, url_for, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse
import time

URL_LENGTH_LIMIT=512
URL_GEN_ERROR = {
	"badurl" : "Bad URL. The URL show start with 'http://' or 'https://' and it should have a valid netloc, ending with '.com', for example.",
	"urllen" : "Invalid URL Length. The URL is either too long or non-existant.",
	"inval" : "Invalid URL. The URL passed has not been recognized."
}

app = Flask("url-shortener")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///short_urls.db"
db = SQLAlchemy(app)

class URLShortener(db.Model):
	plain_url = db.Column(db.String(URL_LENGTH_LIMIT), primary_key=True, unique=True, nullable=False)
	short_url = db.Column(db.String(64), primary_key=False, unique=True, nullable=False)

	def __init__(self, url : str):
		self.plain_url = url
		self.short_url = str(hex(int(time.time() * 1000))).replace("0x", "")

def check_url(url : str):
	valid_protocols = ["http://", "https://"]
	protocol = ""
	for proto in valid_protocols:
		if url.startswith(proto):
			protocol = proto
	if protocol not in valid_protocols:
		return False
	
	url = url[len(protocol):]
	nl = url.find(".")

	return url[nl] != url[-1]

@app.route("/", methods=["GET", "POST"])
def index():
	if request.method == "POST":
		url = request.form["url"]
		if url == None or not check_url(url):
			return redirect(url_for("generated", short_url="badurl"))
		if len(url) == 0 or len(url) > URL_LENGTH_LIMIT:
			return redirect(url_for("generated", short_url="urllen"))
		duplicated = URLShortener.query.filter_by(plain_url=url).first()
		if duplicated:
			return redirect(url_for("generated", short_url=duplicated.short_url))
		gen_url = URLShortener(url)
		db.session.add(gen_url)
		db.session.commit()
		return redirect(url_for("generated", short_url=gen_url.short_url))
	else:
		return render_template("index.html")

@app.route("/<short_url>")
def url_redirect(short_url):
	url = URLShortener.query.filter_by(short_url=short_url).first()
	if not url:
		return redirect(url_for("generated", short_url="inval"))
	return redirect(url.plain_url)

@app.route("/generated/<short_url>", methods=["GET"])
def generated(short_url):
	if short_url not in URL_GEN_ERROR and not URLShortener.query.filter_by(short_url=short_url).first():
		return render_template("generated.html", short_url="inval", errlist=URL_GEN_ERROR)
	else:
		return render_template("generated.html", short_url=short_url, errlist=URL_GEN_ERROR)

if __name__ == "__main__":
	db.create_all()
	app.run(debug=True)