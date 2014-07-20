#!/usr/bin/env python

from app import app

if __name__ == "__main__":

    import sys

    debug = False

    if "--dev" not in sys.argv:
        debug = True

    app.run(debug=debug, host='localhost', port=5000)
