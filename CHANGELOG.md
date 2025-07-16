# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - Wallets, UI, and Education - 2025-07-14

This version marks a major evolution from a simple API to a full-fledged educational tool with a rich user interface and proper cryptographic handling.

### Added
-   **Interactive Educational Dashboard**: A comprehensive `streamlit` application (`src/dashboard.py`) that guides users through blockchain concepts step-by-step.
-   **Cryptographic Wallets**: New `Wallet` class (`src/wallet.py`) using ECDSA (`cryptography` library) to generate public/private key pairs.
-   **Transaction Signing**: Transactions are now cryptographically signed by the sender's private key and verified by the network using the public key.
-   **Transaction Simulator**: A new script (`src/simulation.py`) to generate a continuous stream of random, valid transactions to simulate a live network.
-   **Network Graph Visualization**: A new `/network/graph` endpoint that uses `pyvis` to generate an interactive graph of the peer-to-peer network.
-   **Pending Transactions Endpoint**: A new `/transactions/pending` endpoint to view transactions in the mempool before they are mined.
-   **Unit Tests**: Added tests for the `Wallet` class (`tests/test_wallet.py`) to ensure signing and verification work correctly.
-   **Modern Packaging**: Migrated to a `pyproject.toml` and `src` layout for modern, standardized packaging.
-   **Conda Environment**: Added `environment.yml` for easy and reliable dependency management.

### Changed
-   **Project Structure**: Reorganized into a `src` layout. `blockchain.py` is now part of the `simple_blockchain` package.
-   **Dependencies**: Removed `requirements.txt` in favor of `pyproject.toml` and `environment.yml`.
-   **README**: Completely rewritten to reflect the new features, architecture, and educational focus.

## [0.1.0] - Initial Release- 2019-05-23

### Added
-   Initial `Blockchain` class with core functionality for blocks and transactions.
-   Proof-of-work algorithm (`proof_of_work`, `validate_proof`).
-   Flask API for `/mine`, `/chain`, `/nodes/register`, and `/nodes/resolve`.
-   Consensus algorithm to resolve conflicts by selecting the longest valid chain (`resolve_conflicts`).
-   Genesis block creation on initialization.
-   Ability to run the node on a configurable port via command-line arguments.