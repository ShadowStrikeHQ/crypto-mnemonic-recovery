import argparse
import logging
import os
import secrets
import sys
from typing import List, Optional

# Import the BIP39 wordlist (English is the standard)
# You may need to adjust the path based on your project structure
try:
    from mnemonic import Mnemonic
except ImportError:
    print("Error: 'mnemonic' library not found.  Please install it using 'pip install mnemonic'")
    sys.exit(1)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    parser = argparse.ArgumentParser(description="Recovers a BIP39 mnemonic phrase from potentially corrupted or partial seeds.")

    # Add arguments for partial or corrupted mnemonic
    parser.add_argument("--partial_mnemonic", type=str, help="The partial or corrupted mnemonic phrase (space-separated).  Use '?' for missing words.", required=False)
    parser.add_argument("--num_missing", type=int, help="Number of missing words in the mnemonic. Use only if --partial_mnemonic has '?' characters", required=False, default=0)
    parser.add_argument("--wordlist_path", type=str, help="Path to the BIP39 wordlist file (optional). Defaults to the internal BIP39 wordlist", required=False) # Not fully implemented but included for potential expansion.
    parser.add_argument("--language", type=str, help="The mnemonic language to use (default: english).", required=False, default="english")
    parser.add_argument("--max_attempts", type=int, help="The maximum number of attempts to generate a valid mnemonic.", required=False, default=10000)
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.", required=False)


    return parser



def generate_all_possible_mnemonics(partial_mnemonic: str, missing_count: int, language: str) -> List[str]:
    """
    Generates a list of possible mnemonics given a partial mnemonic and the number of missing words.
    This is the CORE algorithm.
    Args:
        partial_mnemonic: The partial mnemonic with '?' representing missing words.
        missing_count: The number of missing words denoted by '?' in the partial_mnemonic.
        language: the language of the mnemonic

    Returns:
        A list of strings, where each string is a potential mnemonic phrase.
    """
    mnemo = Mnemonic(language)

    wordlist = mnemo.wordlist
    partial_words = partial_mnemonic.split()
    unknown_indices = [i for i, word in enumerate(partial_words) if word == '?']

    if len(unknown_indices) != missing_count:
        raise ValueError(f"The number of '?' characters ({len(unknown_indices)}) must match the num_missing argument ({missing_count}).")


    possible_mnemonics = []

    def generate_recursive(current_mnemonic: List[str], index: int):
        """Recursive helper function to build mnemonic phrases."""
        if index == len(unknown_indices):
            # Base case: all missing words have been filled in.
            possible_mnemonics.append(" ".join(current_mnemonic))
            return

        unknown_index = unknown_indices[index]

        for word in wordlist:
            current_mnemonic[unknown_index] = word
            generate_recursive(current_mnemonic, index + 1)

    # Initialize the current mnemonic with the known words.
    current_mnemonic = partial_words[:]

    generate_recursive(current_mnemonic, 0)

    return possible_mnemonics


def is_valid_mnemonic(mnemonic_phrase: str, language: str) -> bool:
    """
    Validates a BIP39 mnemonic phrase by checking its checksum.

    Args:
        mnemonic_phrase: The mnemonic phrase to validate.
        language: The language of the mnemonic

    Returns:
        True if the mnemonic phrase is valid, False otherwise.
    """

    try:
        mnemo = Mnemonic(language)
        mnemo.to_seed(mnemonic_phrase, passphrase="")  # Passphrase can be left empty

        # If it reaches here without raising an exception, it's valid based on BIP39 checksum
        return True
    except Exception as e:
        logging.debug(f"Mnemonic validation failed: {e}")  # Log the exception for debugging
        return False



def main():
    """
    Main function to parse arguments, recover the mnemonic, and print the results.
    """
    parser = setup_argparse()
    args = parser.parse_args()


    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug mode enabled.")



    if not args.partial_mnemonic:
       print("Error: Please provide a partial mnemonic phrase using the --partial_mnemonic argument.")
       sys.exit(1)


    try:
        possible_mnemonics = generate_all_possible_mnemonics(args.partial_mnemonic, args.num_missing, args.language)

        valid_mnemonics = []
        for mnemonic in possible_mnemonics:
            if is_valid_mnemonic(mnemonic, args.language):
                valid_mnemonics.append(mnemonic)


        if valid_mnemonics:
            print("Possible Valid Mnemonic Phrases:")
            for mnemonic in valid_mnemonics:
                print(mnemonic)
        else:
            print("No valid mnemonic phrases could be recovered.")



    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Usage Examples:
#
# 1. Recover a mnemonic with one missing word:
#    python main.py --partial_mnemonic="abandon ability able about above absent absorb abstract absurd abuse access ? account" --num_missing 1
#
# 2. Recover a mnemonic with two missing words:
#    python main.py --partial_mnemonic="abandon ability able about above absent absorb abstract absurd abuse ? ? account" --num_missing 2
#
# 3. Using debug mode to see more details:
#    python main.py --partial_mnemonic="abandon ability able about above absent absorb abstract absurd abuse ? ? account" --num_missing 2 --debug
#
# Notes:
# - The speed of recovery depends heavily on the number of missing words.  Each missing word significantly increases the search space.
# - Consider the --max_attempts argument to control the maximum number of iterations performed.
# - Thoroughly test and review before using in any production or critical system.