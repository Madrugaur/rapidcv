"""Simple Flask server to handle evoking the RapidCV library"""
from argparse import Namespace
import os
from flask import Flask, request

from rapidcv import RapidCV
from download_folder import get_download_folder

app = Flask(__name__)


@app.get("/generate")
def generate_coverletter():
    """_summary_

    Returns:
        _type_: _description_
    """
    if "company" not in request.args or "role" not in request.args:
        return ({"status": "missing args"}, 400, {})

    output_path = os.path.join(
        get_download_folder(), f"{request.args['company']}_cv.docx"
    )

    args = Namespace(
        template=f"{os.path.join(os.path.dirname(os.getcwd()), 'cvs', 'template.docx')}",
        output=output_path,
        interactive=False,
        substitutions={
            "company": request.args["company"],
            "role": request.args["role"],
        },
    )

    RapidCV().main(args)
    return ({"status": "ok", "path": output_path}, 200, {})


if __name__ == "__main__":
    app.run(debug=True, port=64000)
