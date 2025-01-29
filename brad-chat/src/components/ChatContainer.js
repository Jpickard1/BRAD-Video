import React, { useEffect, useState } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

import "highlight.js/styles/github.css";
import hljs from "highlight.js";

function ChatContainer({ messages, setMessages, setVideoSrc }) {
  useEffect(() => {
    hljs.highlightAll();
  }, [messages]);

  const handleSendMessage = async (message) => {
    setMessages([...messages, { id: Date.now(), text: message, sender: 'user' }]);

    console.log("1. setting messages", message);

    let data = { "message": message };
    try {
      // Call the backend API using fetch
      const response = await fetch('/api/invoke/chat', {
        method: 'POST', // or 'GET' depending on your API
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data), // Send the form data as a JSON payload
      });
      console.log("2. got response", response);

      // Parse the JSON response
      const result = await response.json();
      const bot_response = result['response'];
      const video_url = result['video']; // Extract the video link from the response
      const start_time = result['time']; // Extract the video link from the response
      console.log("-- video_url", video_url);
      console.log("-- start_time", start_time);

      // Update messages
      setMessages((messages) => [...messages, { id: Date.now(), text: bot_response, sender: 'bot' }]);

      // Pass the video link to the parent component
      if (video_url) {
        setVideoSrc(`https://www.youtube.com/embed/${video_url}?autoplay=1&start=${start_time}`);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="chat-container">
      <MessageList messages={messages} />
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  );
}

export default ChatContainer;
