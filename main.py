__author__ = 'kecorbin'
import logging
from acimigrate import app

app.secret_key = '1234'
app.run(host='0.0.0.0', port=8000, debug=False)
