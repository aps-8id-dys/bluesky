# 8ID Bluesky Instrument

**Caution**:  If you will use the [bluesky queueserver (QS)](./qserver.md), note
that _every_ Python file in this directory will be executed when QS starts the
RunEngine. Don't add extra Python files to this directory.  Instead, put them in
`user/` or somewhere else.

Contains:

description | item(s)
--- | ---
Introduction | [`intro2bluesky.md`](https://bcda-aps.github.io/bluesky_training/reference/_intro2bluesky.html)
IPython console startup | [`./console/`](console/README.md)
Bluesky queueserver `*QS*` support | [introduction](./qserver.md)
Instrument package | [`./instrument/`](./instrument/README.md)
Conda environments | [`./environments/`](./environments/README.md)
Unit tests | [`./tests/`](./tests/README.md)
Documentation | [How-to, examples, tutorials, reference](https://bcda-aps.github.io/bluesky_training)
