# Contributing

Start with an issue describing the device, OS, upstream versions, expected behavior,
and sanitized actual result. Never attach keys or unredacted configurations.

Keep this repository an integration kit. Avoid vendoring Hermes, VTuber, Live2D SDKs
or models. Record exact upstream versions when submitting hardware test results.
Do not label a platform supported solely because a mock test passes.

Before a pull request run `python -m unittest discover -s tests -v`. Include meaningful
tests for parsing, authentication handling or protocol changes. Update bilingual
entry points when setup changes. Explain new dependencies and license implications.
