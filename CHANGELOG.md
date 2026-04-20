# Changelog

## [1.0.0] - 2026-04-20
### Version stable officielle
- 13 backends Mobile Money africains
- Wave, Orange Money, MTN MoMo, Moov Money
- Airtel Money, Free Money, M-Pesa
- Wizall Money, Celtiis Cash, YAS Money
- CinetPay, Sama Money, Ecobank
- 79 tests passing
- 90% coverage
- Documentation complète ReadTheDocs
- Admin Django intégré
- Signals, Webhooks, TemplateTags

## [0.4.0] - 2026-04-20
### Ajouté
- Coverage 92% — tests complets sur tous les modules
- Tests utils : create_transaction, update_transaction
- 34 tests passing

## [0.3.0] - 2026-04-20
### Ajouté
- WebhookView — vue générique pour les 4 providers
- urls.py — endpoints webhooks prêts à l'emploi
- templatetags — payment_button et transaction_status_badge
- signals — payment_success, payment_failed, payment_pending
- utils — create_transaction et update_transaction
- 29 tests passing

## [0.2.0] - 2026-04-20
### Ajouté
- Modèle MobileTransaction
- Modèle WebhookLog
- Admin Django avec badges de statut
- Migrations incluses

## [0.1.0] - 2026-04-20
### Ajouté
- Premier release
- Backend Wave CI/SN
- Backend Orange Money CI/SN/CM/BF/ML/GN
- Backend MTN MoMo CI/GH/CM/BJ/SN/UG
- Backend Moov Money CI/BJ/TG/BF/ML/NE
- 26 tests passing

