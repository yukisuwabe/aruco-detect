## Utilities to Detect and Estimate Pose of Aruco Tags

### Installation

It's recommended to use a virtual environment to install the dependencies. I like using [pyenv](https://github.com/pyenv/pyenv). Once you have a virtualenv initialized, install the dependencies:

```python
pip install -r requirements.txt
```

### Usage

Set the parameter for `DICTIONARY` at the top of the `detect.py` file. This should be the dictionary you used to generate the markers, using a generator like [this one](https://chev.me/arucogen/). Then run the command to begin detection:

```python
python detect.py
```