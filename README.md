# Inotia 2 ARM32 — F2 regression testing

This repository currently contains **test infrastructure only**. The F2 IPA is **not uploaded** here.

- Original baseline: `Inotia2_F2_FOREST7_DARKPIT13_SIEGE_TEST_RESIGN_REQUIRED.ipa`
- Original SHA-256: `d8c49b4bbf4e2c9be9ee4b4c015ce26a7cdb7e04257b1e2af41900fc805b3adb`
- Current beta: `Inotia2_F2_FOREST7_7BOSS_IN_ROOMS_NATIVE_BETA_RESIGN_REQUIRED_20261109.ipa`
- Beta SHA-256: `44ad660b7604be51e6231044cfb4faebbf0cfa5209b6945a310187c4059ef71c`

**Important:** The repository is public. Do not upload the full IPA, signing certificates, personal saves, storage data, or private game resources unless you intend to distribute them publicly. Use a private repository or private CI artifact for IPA testing.

Static checks validate ZIP integrity, maps, 7 bosses in rooms 279–285, 8 Forest monster generators and native gate pointers. They **do not** run the ARM32 game engine, combat, skills, loot factory, Save/Continue, or real iPhone 4S/iPad 4 CPU/RAM/FPS measurements.

For this reason, a static PASS must never be called a device PASS. Keep the original F2 baseline and save backup intact.
