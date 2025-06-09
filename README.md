# crypto-mnemonic-recovery
Recovers a BIP39 mnemonic phrase from potentially corrupted or partial seeds using fuzzy matching and statistical analysis. Can attempt reconstruction with missing words or incorrect checksums. - Focused on Basic cryptographic operations

## Install
`git clone https://github.com/ShadowStrikeHQ/crypto-mnemonic-recovery`

## Usage
`./crypto-mnemonic-recovery [params]`

## Parameters
- `-h`: Show help message and exit
- `--partial_mnemonic`: No description provided
- `--num_missing`: Number of missing words in the mnemonic. Use only if --partial_mnemonic has 
- `--wordlist_path`: No description provided
- `--language`: No description provided
- `--max_attempts`: The maximum number of attempts to generate a valid mnemonic.
- `--debug`: Enable debug logging.

## License
Copyright (c) ShadowStrikeHQ
