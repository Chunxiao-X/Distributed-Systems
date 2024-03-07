import xmlrpc.client
from xmlrpc.client import ProtocolError, Fault

# Define the server URL to ensure it matches the address and port of the server
SERVER_URL = "http://localhost:8000"

def add_note():
    try:
        # Prompt user for note details
        topic_name = input("Enter topic name: ")
        note_name = input("Enter note name: ")
        text = input("Enter text: ")
        # Attempt to add the note via the server's add_note method
        result = server.add_note(topic_name, note_name, text)
        if result:
            print("Note added successfully.")
        else:
            print("Failed to add note.")
    except ProtocolError as pe:
        # Handle protocol errors (e.g., unexpected HTTP status codes)
        print(f"A protocol error occurred: URL: {pe.url}, Error code: {pe.errcode}, Error message: {pe.errmsg}")
    except Fault as f:
        # Handle server-side faults (e.g., method execution failures)
        print(f"A server fault occurred: {f}")
    except Exception as e:
        # Catch any unexpected errors
        print(f"An unexpected error occurred: {e}")    

def get_notes_by_topic():
    try:
        # Prompt user for the topic name to fetch notes
        topic_name = input("Enter topic name to fetch notes for: ")
        notes = server.get_notes_by_topic(topic_name)
        if notes:
            # If notes are found, print the topic and each note's details
            print(f"Topic: {topic_name}")  # Added topic name to output
            for note in notes:
                print(f"  Note Name: {note['name']}")
                print(f"  Text: {note['text']}")
                print(f"  Timestamp: {note['timestamp']}\n")
        else:
            print("No notes found for this topic.")
    except ProtocolError as pe:
        # Handle protocol errors
        print(f"A protocol error occurred: URL: {pe.url}, Error code: {pe.errcode}, Error message: {pe.errmsg}")
    except Fault as f:
        # Handle server-side faults
        print(f"A server fault occurred: {f}")
    except Exception as e:
        # Catch any unexpected errors
        print(f"An unexpected error occurred: {e}")

def add_wikipedia_info():
    try:
        # Prompt user for topic and note name for adding Wikipedia info
        topic_name = input("Enter topic name for Wikipedia search: ")
        note_name = input("Enter note name for Wikipedia link: ")
        link = server.add_wikipedia_info(topic_name, note_name)
        if link != "No Wikipedia link found.":
            print(f"Wikipedia link added to the note: {link}")
        else:
            print("No Wikipedia link found for this topic.")
    except ProtocolError as pe:
        # Handle protocol errors
        print(f"A protocol error occurred: URL: {pe.url}, Error code: {pe.errcode}, Error message: {pe.errmsg}")
    except Fault as f:
        # Handle server-side faults
        print(f"A server fault occurred: {f}")
    except Exception as e:
        # Catch any unexpected errors
        print(f"An unexpected error occurred: {e}")

def delete_note():
    try:
        # Prompt user for topic and note name to delete
        topic_name = input("Enter the topic name of the note you want to delete: ")
        note_name = input("Enter the name of the note you want to delete: ")
        result = server.delete_note(topic_name, note_name)
        print(result)
    except ProtocolError as pe:
        # Handle protocol errors
        print(f"A protocol error occurred: URL: {pe.url}, Error code: {pe.errcode}, Error message: {pe.errmsg}")
    except Fault as f:
        # Handle server-side faults
        print(f"A server fault occurred: {f}")
    except Exception as e:
        # Catch any unexpected errors
        print(f"An unexpected error occurred: {e}")

# Main program loop
if __name__ == "__main__":
    # Create a server proxy with the specified URL
    server = xmlrpc.client.ServerProxy(SERVER_URL, allow_none=True)
    
    while True:
        # Display user options
        print("\nOptions:")
        print("1. Add note")
        print("2. Get notes by topic")
        print("3. Add Wikipedia info to topic")
        print("4. Delete a note")
        print("5. Exit")
        choice = input("Enter your choice: ")

        # Execute the chosen option
        if choice == "1":
            add_note()
        elif choice == "2":
            get_notes_by_topic()
        elif choice == "3":
            add_wikipedia_info()
        elif choice == "4":
            delete_note()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
