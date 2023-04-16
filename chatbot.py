import sqlite3
import time
import openai
import subprocess
import signal
import random
import json
import requests
import re
import difflib

min_time = 20
max_time = 90

sleep_time = random.randint(min_time, max_time)

# Load the standard_responses from the JSON
with open("standard_responses.json", "r") as f:
    standard_responses = json.load(f)


# Load the system_messages from the JSON
with open("system_messages.json", "r") as f:
    system_messages = json.load(f)


contact_handle = (
    "123456789"  # Replace with the actual number you want the bot to interract with
)
last_processed_message_id = ""


phone_to_email = {
    contact_handle: "sample@gmail.com",  # Add the actual email address associated with the Apple ID
}


conn = sqlite3.connect(
    f"/Sample/SampleUsername/Library/Messages/chat.db"
)  # Replace with the actual email address associated with the Apple ID
c = conn.cursor()


def fetch_last_n_messages(c, contact_handle, n):
    c.execute(
        f"SELECT m.text, m.is_from_me, m.date, m.ROWID, h.id FROM message m JOIN handle h ON m.handle_id = h.ROWID WHERE m.handle_id IN (SELECT handle_id FROM handle WHERE id='{contact_handle}') ORDER BY m.date DESC LIMIT {n}"
    )

    messages = c.fetchall()

    messages = [msg for msg in messages if msg[0] is not None]

    messages.reverse()

    return messages


last_4_messages = fetch_last_n_messages(c, contact_handle, 4)


def add_to_system_messages(system_messages, fetched_messages, starting_index):
    for i, message_info in enumerate(fetched_messages):
        message_text, is_from_me, _, _, _ = message_info
        role = "assistant" if is_from_me else "user"
        index = starting_index - i - 1
        system_messages.append(
            {"role": role, "content": f"Last message nr. {index}: {message_text}"}
        )
        print(f"Last message nr. {index}, role: {role}, content: {message_text}")
    return system_messages


# Update the system_messages list with the fetched messages
system_messages = add_to_system_messages(system_messages, last_4_messages, 4)


def escape_applescript_characters(text):
    return text.translate(
        str.maketrans({"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t"})
    )


def remove_punctuation_and_symbols(text):
    return re.sub(r"[^a-zA-Z0-9 ]+", "", text)


def calculate_similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def check_for_matching_message(received_message, standard_responses):
    received_message = (
        remove_punctuation_and_symbols(received_message).lower().replace(" ", "")
    )

    for key in standard_responses:
        cleaned_key = remove_punctuation_and_symbols(key).lower().replace(" ", "")
        similarity = calculate_similarity(cleaned_key, received_message)

        if similarity >= 0.65: # Adjust the threshold value in the line `if similarity >= 0.65` to determine the minimum similarity score needed to match a received message to one of the standard responses. Standard responses are stored in the `standard_responses` variable and are used to generate pre-written responses to the user.

            return key
    return None


openai.api_key = "Your API key"

phrases_to_remove = [
    "Here you can add a list of phrases to remove if wanted otherwise leave it empty",
]


def get_openai_response(prompt, system_messages):
    max_retries = 5
    retries = 0

    while retries < max_retries:
        try:
            messages = system_messages.copy()
            messages.append({"role": "user", "content": prompt})

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.6,
                max_tokens=200,
                presence_penalty=1,
                frequency_penalty=1,
            )
            gpt_response = response["choices"][0]["message"]["content"].strip()

            for phrase in phrases_to_remove:
                if phrase in gpt_response:
                    gpt_response = gpt_response.replace(phrase, "")
                if phrase in prompt:
                    prompt = prompt.replace(phrase, "")

            # Remove keyword and everything after them, if wanted otherwise leave blank
            keywords = ["Regards,", "Something you want to remove"]
            for keyword in keywords:
                if keyword in gpt_response:
                    gpt_response = gpt_response.split(keyword)[0]
                    print(gpt_response)
            return gpt_response

        except requests.exceptions.RequestException as e:
            print(f"Exception: {e}")
            if "overloaded" in str(e) and retries < max_retries:
                retries += 1
                print(f"Retrying request ({retries}/{max_retries})")
                time.sleep(15)
                continue
            else:
                print(f"Full response object: {response}")
                return f"Something went wrong... {str(e)}"
        except openai.error.OpenAIError as e:
            print(f"Exception: {e}")
            return "Something went wrong..."
        except Exception as e:
            print(f"Exception: {e}")
            print(f"Full response object: {response}")
            return f"Something went wrong... {str(e)}"


print("Bot started")


def send_imessage(handle, message):
    if message.strip() == "":
        print("Empty response, not sending message.")
        return

    escaped_message = escape_applescript_characters(message)

    for attempt in range(3):
        try:
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    f'tell application "Messages" to send "{escaped_message}" to buddy "{handle}"',
                ]
            )
            print(f"Message sent successfully on attempt {attempt + 1}.")
            break
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            if attempt < 2:
                print("Retrying...")
                time.sleep(1)
            else:
                print("Failed to send message after 3 attempts.")

    sleep_random = random.uniform(6, 12)
    time.sleep(sleep_random)


def signal_handler(signal, frame):
    print("\nExiting gracefully...")
    exit(0)


signal.signal(signal.SIGINT, signal_handler)

print("Sending to " + contact_handle)

time.sleep(sleep_time)

while True:
    try:
        c.execute(
            f"SELECT m.text, m.is_from_me, m.ROWID, h.id FROM message m JOIN handle h ON m.handle_id = h.ROWID WHERE m.handle_id IN (SELECT handle_id FROM handle WHERE id='{contact_handle}') ORDER BY m.date DESC LIMIT 1"
        )
        latest_message_info = c.fetchone()

        if latest_message_info is not None:
            message_text = latest_message_info[0]
            is_from_me = latest_message_info[1]
            current_message_id = latest_message_info[2]
            current_contact_handle = latest_message_info[3]

            if not is_from_me and current_message_id != last_processed_message_id:
                last_processed_message_id = current_message_id
                print(f"Message from {current_contact_handle}: {message_text}")

                gpt_response = None

                matching_key = check_for_matching_message(
                    message_text, standard_responses
                )
                if matching_key is not None:
                    responses = standard_responses[matching_key]
                    gpt_response = random.choice(responses)

                if gpt_response is None:
                    gpt_response = get_openai_response(
                        prompt=message_text, system_messages=system_messages
                    )

                print(f"Response from bot: {gpt_response}")
                send_imessage(current_contact_handle, gpt_response)

                last_4_messages = fetch_last_n_messages(c, contact_handle, 4)
                system_messages = add_to_system_messages(
                    system_messages, last_4_messages, 4
                )

            else:
                print("No new messages")
        else:
            print("No new messages")

        time.sleep(sleep_time)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        if contact_handle is not None:
            send_imessage(contact_handle, "Something went wrong...")
        continue
