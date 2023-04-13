 
  <body>
    <h1>iMessage Chatbot</h1>
    <h2>Description</h2>
    <p>
      This is a Python script that creates an iMessage chatbot using OpenAI's
      chat completion model. The chatbot automatically sends responses to
      incoming messages on iMessage based on the conversation history and the
      available data sources.
    </p>
    <h2>Requirements</h2>
    <ul>
      <li>Python 3</li>
      <li>sqlite3</li>
      <li>OpenAI API key</li>
      <li>Apple ID associated with iMessage</li>
    </ul>
    <h2>Setup</h2>
    <h3>Install Required Libraries</h3>
    <p>
      Install the required libraries by running
      <code>pip3 install -r requirements.txt</code>.
    </p>
    <h3>Add OpenAI API Key</h3>
    <p>
      Add your OpenAI API key in the line
      <code>openai.api_key = "Your API key"</code>.
    </p>
    <h3>Set Contact Phone Number</h3>
    <p>
      Replace the value of the <code>contact_handle</code> variable with the
      phone number you want the bot to interact with.
    </p>
    <h3>Set Apple ID Email Address</h3>
    <p>
      Replace the value of the <code>phone_to_email</code> dictionary with the
      email address associated with your Apple ID.
    </p>
    <h3>Customize Response Files</h3>
    <p>
      Customize the <code>standard_responses.json</code> and
      <code>system_messages.json</code> files to add your own responses and
      system messages.
    </p>
    <h3>Run the Script</h3>
    <p>Run the script using <code>python3 chatbot.py</code>.</p>
    <h2>Usage</h2>
    <p>
      The chatbot will automatically send responses to incoming messages on
      iMessage based on the conversation history and the available data sources.
      You can customize the behavior of the chatbot by modifying the
      <code>get_openai_response</code> function and the data sources used by the
      script.
    </p>
    <h2>Troubleshooting</h2>
    <p>
      If you encounter any issues while running the script, you can try the
      following:
    </p>
    <ul>
      <li>
        Check that your OpenAI API key is valid and has sufficient permissions.
      </li>
      <li>
        Check that your Apple ID is associated with the iMessage account you
        want to use.
      </li>
      <li>
        Check that the <code>chat.db</code> file path in the <code>conn</code>
        variable is correct for your system.
      </li>
      <li>
        Check that the <code>standard_responses.json</code> and
        <code>system_messages.json</code> files are properly formatted and
        contain valid data.
      </li>
    </ul>
    <h2>Credits</h2>
    <p>
      This script was created by Fredrik Haugen. If you have any questions or feedback, please contact me at fredrik@haugendesign.net.
    <p>
    </body>
