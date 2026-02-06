# IF YOU'RE ONE OF MY PLAYERS, DO NOT READ THIS SCRIPT
# AS THE SECRET MSG IS PLAINTEXT.






import streamlit as st
import random
import string
import re

class Message:
    def __init__(self, text):
        self.original_text = text
        self.unique_letters = self._get_unique_letters()
        self.cipher_map = self._create_cipher_map()

    def _get_unique_letters(self):
        """Get all unique letters from the message (case-insensitive)"""
        letters = set()
        for char in self.original_text.lower():
            if char.isalpha():
                letters.add(char)

        # Separate vowels and consonants
        all_letters = list(letters)
        vowels = [l for l in all_letters if l in 'aeiou']
        consonants = [l for l in all_letters if l not in 'aeiou']

        # Sort vowels in order a, e, i, o, u
        vowel_order = ['a', 'e', 'i', 'o', 'u']
        sorted_vowels = [v for v in vowel_order if v in vowels]

        # Scramble consonants
        random.seed(42)
        random.shuffle(consonants)

        # Return vowels first, then scrambled consonants
        return sorted_vowels + consonants

    def _create_cipher_map(self):
        """Create a mapping from letters to strange ASCII characters"""
        # Vowels get dice characters (or numeric representations)
        vowel_map = {
            'a': '⚀',  # Dice 1
            'e': '⚁',  # Dice 2
            'i': '⚂',  # Dice 3
            'o': '⚃',  # Dice 4
            'u': '⚄',  # Dice 5
        }


        # Consonants get cryptic characters
        consonant_chars = ['§', '¶', '†', '‡', '•', '◊', '∆', '∑', '∏', '√',
                           '∫', '≈', '≠', '≤', '≥', '÷', '¥', '∞', '∂',
                           '∇', '⊕', '⊗', '⊥', '∩', '∪', '⊂']

        # Shuffle consonant chars for randomness
        random.seed(42)
        random.shuffle(consonant_chars)

        cipher_map = {}
        consonant_index = 0

        for letter in self.unique_letters:
            if letter in vowel_map:
                cipher_map[letter] = vowel_map[letter]
            else:
                cipher_map[letter] = consonant_chars[consonant_index % len(consonant_chars)]
                consonant_index += 1

        return cipher_map

    def encode(self):
        """Convert the message to encoded form"""
        encoded = []
        for char in self.original_text:
            if char.lower() in self.cipher_map:
                # Preserve case by checking if original was uppercase
                encoded.append(self.cipher_map[char.lower()])
            else:
                encoded.append(char)
        return ''.join(encoded)

    def decode(self, user_guesses):
        """Decode the message based on user guesses"""
        decoded = []
        for char in self.original_text:
            if char.lower() in user_guesses:
                # Use the user's guess, preserving original case
                guess = user_guesses[char.lower()]
                if char.isupper():
                    decoded.append(guess.upper() if guess else char)
                else:
                    decoded.append(guess if guess else char.lower())
            elif char.isalpha():
                # Not yet guessed, show the cipher character
                decoded.append(self.cipher_map[char.lower()])
            else:
                decoded.append(char)
        return ''.join(decoded)

    def get_red_words(self, user_guesses):
        """Find words that have only one unknown letter"""
        # Split by whitespace and newlines
        lines = self.original_text.split('\n')
        red_word_positions = set()

        for line in lines:
            words = line.split()
            for word in words:
                alpha_word = re.sub('[^A-Za-z0-9]+', '', word)
                # Count unknown letters (letters without guesses) in this word
                unknown_count = 0

                for char in alpha_word:
                    if (char.lower() not in user_guesses or not user_guesses[char.lower()]):
                        unknown_count += 1
                #st.write(f"{word}, {unknown_count}")
                # If exactly one letter is unknown, mark this word for red
                if (unknown_count == 1) and (len(alpha_word) != 2):
                    # Store the actual word with punctuation for matching
                    red_word_positions.add(word)

        return red_word_positions

    def format_decoded_message(self, user_guesses):
        """Format the decoded message with HTML highlighting for red words"""
        red_word_set = self.get_red_words(user_guesses)

        # Process line by line to preserve line breaks
        lines = self.original_text.split('\n')
        formatted_lines = []

        for line in lines:
            words = line.split()
            formatted_words = []

            for word in words:
                decoded_word = []
                for char in word:
                    if char.lower() in user_guesses and user_guesses[char.lower()]:
                        # User has made a guess for this letter
                        guess = user_guesses[char.lower()]
                        if char.isupper():
                            decoded_word.append(guess.upper())
                        else:
                            decoded_word.append(guess)
                    elif char.isalpha():
                        # Show cipher character
                        decoded_word.append(self.cipher_map[char.lower()])
                    else:
                        # Punctuation, numbers, etc.
                        decoded_word.append(char)

                decoded_word_str = ''.join(decoded_word)
                if re.sub('[^A-Za-z0-9]+', '', decoded_word_str).lower() == re.sub('[^A-Za-z0-9]+', '', word).lower():
                    formatted_words.append(decoded_word_str)
                # Check if this word should be red (words with only 1 unknown letter)
                elif word in red_word_set:
                    formatted_words.append(
                        f'<span style="color: #ff4444; font-weight: bold;">{decoded_word_str}</span>')
                else:
                    formatted_words.append(
                        f'<span style="color: #9c5a14; font-weight: bold;">{decoded_word_str}</span>')
                    #formatted_words.append(decoded_word_str)

            formatted_lines.append(' '.join(formatted_words))

        return '<br>'.join(formatted_lines)



# Streamlit app
st.set_page_config(page_title="Decoding the Message", layout="wide")
st.title("🔐 Decoding the Message")

# The secret message
SECRET_MESSAGE = """Your name is Gunnar. You are a flesh dwarf, so mask your voice with the "deep male number four" audio.
The adventures are staying at Brenda's tavern and inn. Burn it. Make sure you are seen. Turn Gruin against the flesh dwarves. They cannot be allowed to heal this divide we've created.
Do not be captured!"""

# Initialize the message object
if 'message_obj' not in st.session_state:
    st.session_state.message_obj = Message(SECRET_MESSAGE)

message_obj = st.session_state.message_obj

# Initialize user guesses
if 'guesses' not in st.session_state:
    st.session_state.guesses = {letter: '' for letter in message_obj.unique_letters}

# Create two columns
col1, col2 = st.columns([1.5, 1])
key_idx = 0
with col2:
    st.header("Letter Decoder")
    st.subheader("Enter your guesses for each cipher character:")

    letters = message_obj.unique_letters

    # First show vowels (dice characters) in their own row
    st.markdown("## **Dice 1-5:**")
    vowel_cols = st.columns(5)
    vowel_count = 0

    for letter in letters:
        if letter in 'aeiou':
            cipher_char = message_obj.cipher_map[letter]

            with vowel_cols[vowel_count]:
                st.markdown(
                    f"""
                    <div style="
                        text-align: center;
                        font-size: 32px;
                        font-weight: 700;
                        margin-bottom: -10px;
                    ">
                        {cipher_char}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                guess = st.text_input(
                    label=f"{cipher_char}",
                    value=st.session_state.guesses[letter],
                    max_chars=1,
                    key=f"nice_try_ben_{key_idx}",
                    label_visibility="collapsed"
                )
                key_idx += 1

                # Update the guess
                if guess:
                    st.session_state.guesses[letter] = guess.lower()
                else:
                    st.session_state.guesses[letter] = ''

            vowel_count += 1

    st.markdown("---")
    st.markdown("## **Non-Dice characters**")

    # Then show consonants in scrambled order
    consonants = [l for l in letters if l not in 'aeiou']
    cols_per_row = 5

    for i in range(0, len(consonants), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(consonants):
                letter = consonants[idx]
                cipher_char = message_obj.cipher_map[letter]

                with cols[j]:
                    st.markdown(
                        f"""
                        <div style="
                            text-align: center;
                            font-size: 32px;
                            font-weight: 700;
                            margin-bottom: -10px;
                        ">
                            {cipher_char}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    guess = st.text_input(
                        label=f"{cipher_char}",
                        value=st.session_state.guesses[letter],
                        max_chars=1,
                        key=f"nice_try_ben_{key_idx}",
                        label_visibility="collapsed"
                    )
                    key_idx += 1

                    # Update the guess
                    if guess:
                        st.session_state.guesses[letter] = guess.lower()
                    else:
                        st.session_state.guesses[letter] = ''
with col1:
    st.header("Encoded Message")

    # Display the decoded message with red highlighting
    formatted_message = message_obj.format_decoded_message(st.session_state.guesses)
    st.markdown(
        f'<div style="background-color: #dedede; padding: 20px; border-radius: 5px; font-family: monospace; font-size: 32px; line-height: 1.6;">{formatted_message}</div>',
        unsafe_allow_html=True)

    st.info("💡 Words highlighted in **red** have only one unknown letter! Two letter words are not highlighted.")

# Show progress
total_letters = len(message_obj.unique_letters)
guessed_letters = sum(1 for g in st.session_state.guesses.values() if g)
st.progress(guessed_letters / total_letters)
st.write(f"Progress: {guessed_letters}/{total_letters} letters guessed")

# Check if solved
if guessed_letters == total_letters:
    decoded = message_obj.decode(st.session_state.guesses)
    if decoded.lower() == SECRET_MESSAGE.lower():
        st.success("🎉 Congratulations! You've decoded the message!")
        st.balloons()