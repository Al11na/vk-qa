# REST API and contract tests

Pytest tests for the public JSONPlaceholder API. The OpenAPI contract is in `openapi.yaml`; request and response schemas are checked with `jsonschema`.

## Run

Requires Python 3.10 or newer and internet access.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -v
```

## Coverage

- Fetching the posts collection and a single post, including response validation against the OpenAPI schema.
- Creating a post and validating the response contract.
- An existing boundary ID and negative cases for out-of-range and malformed IDs.
- Required request fields in the OpenAPI schema.

JSONPlaceholder is a demo API: `POST /posts` returns a simulated resource but does not persist it or validate the submitted fields server-side. The empty-string test documents this mock behavior; it does not claim to test server-side validation.
