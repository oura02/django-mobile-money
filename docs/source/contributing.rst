Contribution
============

Merci de contribuer à django-mobile-money !

Installation pour le développement
------------------------------------

.. code-block:: bash

   git clone https://github.com/oura02/django-mobile-money.git
   cd django-mobile-money
   uv sync

Lancer les tests
----------------

.. code-block:: bash

   uv run pytest -v
   uv run coverage run -m pytest
   uv run coverage report

Ajouter un backend
------------------

1. Crée ``django_mobile_money/backends/mon_backend.py``
2. Hérite de ``BasePaymentBackend``
3. Implémente les 3 méthodes
4. Ajoute dans ``backends/__init__.py``
5. Ajoute les tests dans ``tests/test_mon_backend.py``
6. Coverage minimum : 90%

Ouvre une Pull Request sur GitHub.