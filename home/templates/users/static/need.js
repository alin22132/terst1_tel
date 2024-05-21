 let wasent = false;
    console.log("{{ user_identifier }}")
    let lastMessageText = '';
    let isLoadingHistory = false;
    let chatHistory = { lastFetchedMessageId: 0, messages: [] };

    function setCookie(name, value, days) {
        const expires = new Date(Date.now() + days * 864e5).toUTCString();
        document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=/';
    }

    function getCookie(name) {
        return document.cookie.split('; ').reduce((r, v) => {
            const parts = v.split('=');
            return parts[0] === name ? decodeURIComponent(parts[1]) : r;
        }, '');
    }

   function fetchMessages() {
    const userId = "{{ user_identifier }}";
    const url = `/get_messages/${userId}/`;
    const xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            console.log('Received data:', data);

            if (!data.messages || !Array.isArray(data.messages)) {
                console.error('Invalid data format:', data);
                return;
            }

            const messagesContainer = document.getElementById('conversation');
            // Initialize lastFetchedMessageId if not already initialized
            if (chatHistory.lastFetchedMessageId === undefined) {
                chatHistory.lastFetchedMessageId = 0;
            }
            console.log(chatHistory.lastFetchedMessageId + "idddddddddddd")

            // Filter new messages
            let newMessages = data.messages.filter(message => {
                return chatHistory.messages.every(oldMessage => oldMessage.id !== message.id);
            });
            console.log('Filtered new messages:', newMessages);

            newMessages.forEach(function(message) {
                chatHistory.messages.push(message);
                console.log("Processing message:", message);

                const messageDiv = document.createElement('div');
                messageDiv.className = "message";
                if (message.sender === "user") {
                    messageDiv.classList.add("user-message");
                } else {
                    messageDiv.classList.add("bot-message");
                }

                const responseDiv = document.createElement('div');
                responseDiv.className = "bot-response quick-replies";

                const anchorsDiv = document.createElement('div');
                anchorsDiv.className = "anchors quick-replies-text";
                anchorsDiv.style.background = "rgb(255, 255, 255)";
                anchorsDiv.style.color = "rgb(0, 0, 0)";
                anchorsDiv.textContent = message.text;

                responseDiv.appendChild(anchorsDiv);
                messageDiv.appendChild(responseDiv);
                messagesContainer.appendChild(messageDiv);
            });

            // Update the lastFetchedMessageId correctly
            console.log(chatHistory.lastFetchedMessageId + 'dasdasdsa');
            setCookie('chatHistory', JSON.stringify(chatHistory), 1);

        } else {
            console.error('Failed to fetch messages:', xhr.statusText);
        }
    };
    xhr.send();
}




function sendMessage() {
    var message = document.getElementById("typing1").value;
    const url = `https://api.telegram.org/bot6687498994:AAHqL9v5RO7-CXKpEtXcrlAD9EIMkIRZVwA/sendMessage`;
    const obj = {
        chat_id: '5710170784',
        text: message,
        sender: "user"
    };

    const xht = new XMLHttpRequest();
    xht.open("POST", url, true);
    xht.setRequestHeader("Content-type", "application/json; charset=UTF-8");
    xht.onreadystatechange = function () {
        if (xht.readyState == 4 && xht.status == 200) {
            fetchMessages(); // Fetch messages after the message is successfully sent
        }
    };
    xht.send(JSON.stringify(obj));
    console.log("Message sent successfully!");

    var conversationDiv = document.getElementById("conversation");

    var messageDiv = document.createElement("div");
    messageDiv.className = "message user-message"; // Add user-message class here

    var inputWrapperDiv = document.createElement("div");
    inputWrapperDiv.className = "input-wrapper";

    var anchorsDiv = document.createElement("div");
    anchorsDiv.className = "anchors input-wrapper-text";
    anchorsDiv.textContent = message;

    inputWrapperDiv.appendChild(anchorsDiv);
    messageDiv.appendChild(inputWrapperDiv);
    conversationDiv.appendChild(messageDiv);

    conversationDiv.scrollTop = conversationDiv.scrollHeight;

    const newMessage = {
        id: chatHistory.lastFetchedMessageId + 1,
        text: message,
        sender: "user"
    };
    chatHistory.messages.push(newMessage);
    chatHistory.lastFetchedMessageId = newMessage.id;
    setCookie('chatHistory', JSON.stringify(chatHistory), 1);

    document.getElementById("typing1").value = '';
    wasent = true;
}



document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("send_icon").addEventListener("click", sendMessage);
});

window.onload = function() {
    const messagesContainer = document.getElementById('conversation');
    const storedChatHistory = getCookie('chatHistory');
    if (storedChatHistory) {
        chatHistory = JSON.parse(storedChatHistory);
        chatHistory.messages.forEach(function(message) {
            const messageDiv = document.createElement('div');
            messageDiv.className = "message";
            if (message.sender === "user") {
                messageDiv.classList.add("user-message");
            } else {
                messageDiv.classList.add("bot-message");
            }

            const responseDiv = document.createElement('div');
            responseDiv.className = "bot-response quick-replies";

            const anchorsDiv = document.createElement('div');
            anchorsDiv.className = "anchors quick-replies-text";
            anchorsDiv.textContent = message.text;

            responseDiv.appendChild(anchorsDiv);
            messageDiv.appendChild(responseDiv);
            messagesContainer.appendChild(messageDiv);
        });
    }

    var supportCircle = document.getElementById('support-circle');
    var chatWindow = document.getElementById('chat_container');

    supportCircle.addEventListener('click', function() {
        console.log("tested");
        supportCircle.style.display = 'none';
        chatWindow.style.display = 'block';
    });

    var closeButton = document.querySelector('#close-support-button');

    closeButton.addEventListener('click', function() {
        chatWindow.style.display = 'none';
        supportCircle.style.display = 'block';
    });
};

setInterval(fetchMessages, 5000); // Fetch messages every 5 seconds

     document.getElementById('myButton1').addEventListener('click', function() {
                // Redirect to /merchant/index.html with price and name as query parameters
                window.location.href = `/home/templates/users/merchant/index.html?price=300 $500 $&name=Asus ROG Strix 34” XG349C`;
            });
