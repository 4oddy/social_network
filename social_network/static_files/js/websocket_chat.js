const group_name = JSON.parse(document.getElementById('group_name').textContent);
const group_type = JSON.parse(document.getElementById('group_type').textContent);
const chat = document.querySelector('#chat_messages');

        const chatSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/chatting/'
            + group_type + '/'
            + group_name
            + '/'
        );

        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            chat.innerHTML += `<p> <a href="${data.sender_dict['profile_url']}"> <img src="${data.sender_dict['image_url']}" style="    width: 60px;
    height: 60px;
    border-radius: 100px;"> </a> ${data.sender_dict['username']}: ${data.message} </p> <p style="padding-right: 20px;" align="right"> ${data.sender_dict['date']} </p>`
        };

        chatSocket.onclose = function(e) {
            console.error('Chat closed unexpectedly');
        };

        document.querySelector('#chat-message-input').focus();
        document.querySelector('#chat-message-input').onkeyup = function(e) {
            if (e.keyCode === 13) {  // enter, return
                document.querySelector('#chat-message-submit').click();
            }
        };

        document.querySelector('#chat-message-submit').onclick = function(e) {
            const messageInputDom = document.querySelector('#chat-message-input');
            const message = messageInputDom.value.replace(/(<([^>]+)>)/gi, "");;

            if (message.trim().length > 0) {
                chatSocket.send(JSON.stringify({
                    'message': message
                }));
                messageInputDom.value = '';
            }
        };