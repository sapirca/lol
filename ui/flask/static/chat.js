document.addEventListener('DOMContentLoaded', () => {
    const chatMessagesDiv = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');

    function displayMessage(sender, text) {
        const messageElement = document.createElement('div');
        messageElement.textContent = `${sender}: ${text}`;
        chatMessagesDiv.appendChild(messageElement);
        chatMessagesDiv.scrollTop = chatMessagesDiv.scrollHeight; // Scroll to bottom
    }

    async function sendMessage() {
        const messageText = messageInput.value.trim();
        if (messageText) {
            try {
                await fetch('/send_message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: messageText }),
                });
                messageInput.value = '';
                // Fetch messages immediately after sending to show user's message and echo
                fetchMessages();
            } catch (error) {
                console.error('Error sending message:', error);
                displayMessage('Error', 'Could not send message.');
            }
        }
    }

    async function fetchMessages() {
        try {
            const response = await fetch('/get_messages');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const messages = await response.json();
            chatMessagesDiv.innerHTML = ''; // Clear existing messages
            messages.forEach(msg => {
                displayMessage(msg.sender, msg.text);
            });
        } catch (error) {
            console.error('Error fetching messages:', error);
            // Don't display error in chat window to avoid clutter during polling
        }
    }

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Fetch messages periodically
    setInterval(fetchMessages, 2000); // Poll every 2 seconds

    // Initial fetch of messages when the page loads
    fetchMessages();
});
