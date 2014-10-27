import flask
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import random
import io
import urllib
import urllib.parse

app = flask.Flask(__name__)

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/about")
def about():
    return flask.render_template("about.html")

@app.route("/video")
def video():
    video_id = flask.request.args.get("video_id")
    if "youtube" in video_id:
        url = urllib.parse.urlparse(video_id)
        query = dict(urllib.parse.parse_qsl(url[4]))
        video_id = query["v"]
    return flask.render_template("video.html", video_id=video_id)

@app.errorhandler(404)
def not_found(error):
    return flask.render_template("error.html", error=error)

@app.route('/plot.png')
def plot():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)

    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]

    axis.plot(xs, ys)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = flask.make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

if __name__ == "__main__":
    app.run(debug=True)
