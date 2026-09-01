# Repository instructions for AI agents

This repository is the reference implementation for Open Hardware Agent Lab.

Before changing code, read:

1. `README.md`
2. `docs/ARCHITECTURE.md`
3. `docs/PROJECT_LOG.md`
4. applicable records under `docs/decisions/`

## Non-negotiable rules

- Simulation is the default. Never silently select a real hardware driver.
- A model or harness must never be the real-time motor-control loop.
- Safety limits must be enforced inside the device driver, not only in prompts or agent policy.
- Real motion requires an explicit device enable, an apply flag, and a separate confirmation.
- Emergency stop is monotonic: triggering it disables motion; clearing it requires explicit confirmation and must not re-enable actuators.
- Do not claim official MHS compatibility until a public specification or authorized preview SDK has been implemented and verified.
- Keep the core model-agnostic. Claude, DeepSeek Harness and other agent runtimes belong in adapters.
- Do not commit credentials, serial numbers, private lab data or LifeTrace/screen-memory content.
- Do not weaken or remove safety tests to make an integration pass.

## Change workflow

- Record material architectural choices as an ADR in `docs/decisions/`.
- Add a dated entry to `docs/PROJECT_LOG.md` when a milestone is reached.
- Run `uv run pytest` for Python changes.
- Test new real-hardware code in this order: pure unit test, simulator, read-only device connection, disabled write dry-run, supervised low-speed motion.
- Use normalized joint coordinates only in simulation. Real hardware must use its calibrated limits and collision model.

## Public-repository hygiene

- Public documentation may describe reproducible engineering work but must not expose private startup strategy, credentials, customer information or unpublished partner material.
- External code contributions are not accepted until the project license and contributor terms are decided. Issues and design discussions are welcome.
