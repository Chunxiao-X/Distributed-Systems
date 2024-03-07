from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from threading import Thread
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import requests
from datetime import datetime
import os

# Path to the XML database file
DATABASE_FILE = 'db.xml'

# Ensure the XML database exists, create it if it doesn't
def init_db():
    # Check if the file does not exist
    if not os.path.isfile(DATABASE_FILE):
        # Create a root element named 'data'
        root = ET.Element("data")
        # Create an ElementTree object with root
        tree = ET.ElementTree(root)
        # Write the tree to the file
        tree.write(DATABASE_FILE)

# Return a formatted XML string to minimize unnecessary line breaks
def prettify(element):
    # Convert the Element to a string
    rough_string = ET.tostring(element, 'utf-8')
    # Parse the string to a DOM object
    reparsed = minidom.parseString(rough_string)
    # Format the DOM object to a pretty string with indentation
    pretty_string = reparsed.toprettyxml(indent="  ")
    # Use regular expression to remove excess line breaks
    pretty_string = re.sub(r'\n\s*\n', '\n', pretty_string)
    return pretty_string

# Add a note to the XML database
def add_note(topic_name, note_name, text):
    try:
        # Ensure database is initialized
        init_db()
        tree = ET.parse(DATABASE_FILE)
        root = tree.getroot()
        topic_found = False

        # Search for or create the topic
        for topic in root.findall('topic'):
            if topic.attrib['name'] == topic_name:
                topic_found = True
                break

        # Create topic if not found
        if not topic_found:
            topic = ET.SubElement(root, 'topic', {'name': topic_name})

        # Add the note
        note = ET.SubElement(topic, 'note', {'name': note_name})
        ET.SubElement(note, 'text').text = text
        ET.SubElement(note, 'timestamp').text = datetime.now().strftime("%m/%d/%y - %H:%M:%S")

        # Format and write to file
        formatted_xml = prettify(root)
        with open(DATABASE_FILE, "w") as f:
            f.write(formatted_xml)
        return True
    except Exception as e:
        print(f"Error adding note: {e}")
        return False

# Retrieve notes by topic from the XML database
def get_notes_by_topic(topic_name):
    try:
        init_db()
        tree = ET.parse(DATABASE_FILE)
        root = tree.getroot()
        notes_list = []

        # Search for the topic and compile notes
        for topic in root.findall('topic'):
            if topic.attrib['name'] == topic_name:
                for note in topic.findall('note'):
                    text = note.find('text').text
                    timestamp = note.find('timestamp').text
                    notes_list.append({'name': note.attrib['name'], 'text': text, 'timestamp': timestamp})

        return notes_list
    except Exception as e:
        print(f"Error getting notes: {e}")
        return False

# Add Wikipedia summary and link to an existing note
def add_wikipedia_info(topic_name, note_name):
    try:
        init_db()
        tree = ET.parse(DATABASE_FILE)
        root = tree.getroot()
        note_found = False

        # Search for the specified topic and note
        for topic in root.findall('topic'):
            if topic.attrib['name'] == topic_name:
                for note in topic.findall('note'):
                    if note.attrib['name'] == note_name:
                        note_found = True
                        # Fetch Wikipedia summary and link
                        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic_name}"
                        response = requests.get(url)
                        data = response.json()

                        if 'extract' in data and 'content_urls' in data:
                            summary = data['extract']
                            page_url = data['content_urls']['desktop']['page']
                            # Add Wikipedia summary and link as new text elements
                            summary_element = ET.SubElement(note, 'text')
                            summary_element.text = f"Wikipedia Summary: {summary}"
                            link_element = ET.SubElement(note, 'text')
                            link_element.text = f"Wikipedia Link: {page_url}"
                        else:
                            return "No summary or link found on Wikipedia for this topic."
                        break
                if note_found:
                    break

        if not note_found:
            return f"No note named '{note_name}' under topic '{topic_name}' was found."

        # Format and write to file
        formatted_xml = prettify(root)
        with open(DATABASE_FILE, "w") as f:
            f.write(formatted_xml)
        return "Wikipedia summary and link added to note."
    except Exception as e:
        print(f"Error adding Wikipedia info: {e}")
        return False

# Delete a note operation
def delete_note(topic_name, note_name):
    try:
        init_db()
        tree = ET.parse(DATABASE_FILE)
        root = tree.getroot()
        deleted = False

        # Search for and delete the specified note
        for topic in root.findall('topic'):
            if topic.attrib['name'] == topic_name:
                for note in topic.findall('note'):
                    if note.attrib['name'] == note_name:
                        topic.remove(note)
                        deleted = True
                        break
                if deleted:
                    break

        if deleted:
            tree.write(DATABASE_FILE)
            return f"Note '{note_name}' under topic '{topic_name}' was deleted successfully."
        else:
            return "Note or topic not found."
    except Exception as e:
        print(f"Error deleting note: {e}")
        return False

# Add explicit concurrency control or threads in order for the system to efficiently scale and manage multiple requests
# By starting a new thread for each incoming client request, the server is able to process multiple requests in parallel, increasing the ability to handle concurrent requests
class ThreadedXMLRPCServer(SimpleXMLRPCServer):
    def __init__(self, *args, **kwargs):
        SimpleXMLRPCServer.__init__(self, *args, **kwargs)
    
    def process_request_thread(self, request, client_address):
        """Threads that handle each request"""
        try:
            self.finish_request(request, client_address)
            self.shutdown_request(request)
        except Exception as e:
            self.handle_error(request, client_address)
            self.shutdown_request(request)
    
    def process_request(self, request, client_address):
        """Rewrite process_request to use threads"""
        thread = Thread(target=self.process_request_thread, args=(request, client_address))
        thread.daemon = True  # Set up a daemon thread to ensure that the main application can exit when it exits
        thread.start()

# Define the request processor
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create and run the server
with SimpleXMLRPCServer(('localhost', 8000),
                        requestHandler=RequestHandler,
                        allow_none=True) as server:
    server.register_introspection_functions()

    # Register functions
    server.register_function(add_note, 'add_note')
    server.register_function(get_notes_by_topic, 'get_notes_by_topic')
    server.register_function(add_wikipedia_info, 'add_wikipedia_info')
    server.register_function(delete_note, 'delete_note')

    # Server running message
    print("Server is running...")
    server.serve_forever()

if __name__ == "__main__":
    with ThreadedXMLRPCServer(('localhost', 8000), requestHandler=RequestHandler, allow_none=True) as server:
        server.register_introspection_functions()

        server.register_function(add_note, 'add_note')
        server.register_function(get_notes_by_topic, 'get_notes_by_topic')
        server.register_function(add_wikipedia_info, 'add_wikipedia_info')
        server.register_function(delete_note, 'delete_note')

        print("Server is running...")
        server.serve_forever() 