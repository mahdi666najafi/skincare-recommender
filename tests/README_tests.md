# Using pytest and django-pytest

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
pytest
```

## structure:

- `pytest.ini`: initializing pytest
- `tests/conftest.py`: basic assets of the project
- `tests/test_models.py`: testing all models
- `tests/test_recommender.py`: basic tests for recommender system
