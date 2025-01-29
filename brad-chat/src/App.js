import React, { useEffect, useState } from 'react';
import ChatContainer from './components/ChatContainer';
import './App.css';

import "highlight.js/styles/github.css";
import hljs from "highlight.js";

function App() {
  const [messages, setMessages] = useState([]);
  const [videoSrc, setVideoSrc] = useState("https://www.youtube.com/embed/nF59F_igAsE"); // Default video link

  useEffect(() => {
    hljs.highlightAll();
  }, [messages]);

  return (
    <div className="App">
      <header className="App-header">
        <h2>DCMB Seminar RAG by BRAD {String.fromCodePoint('0x1f916')}</h2>
      </header>
      <div className="main-content">
        {/* YouTube Video on the right */}
        <div className="video-container">
          <iframe
            src={videoSrc} // Dynamically update the video source
            title="YouTube video"
            allowFullScreen
          ></iframe>
        </div>
        {/* Chat Container on the left */}
        <ChatContainer
          messages={messages}
          setMessages={setMessages}
          setVideoSrc={setVideoSrc} // Pass the videoSrc setter to ChatContainer
        />
      </div>
    </div>
  );
}

export default App;
