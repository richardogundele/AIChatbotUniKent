import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './index.css';

// SVG Icons to match the original design
const Icons = {
  Robot: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>,
  Accessibility: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="8" r="1.5"/><path d="M16 12H8"/><path d="M12 12v5"/><path d="M12 17l-1.5 2"/><path d="M12 17l1.5 2"/></svg>,
  Calendar: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>,
  Camp: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 21h18"/><path d="M12 3l9 18"/><path d="M12 3L3 21"/><path d="M12 11v10"/></svg>,
  Home: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>,
  Mortarboard: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>,
  Party: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 16L3 21l5-2"/><path d="M21 3l-6 6"/><path d="M15 9l-4 4"/><path d="M11 13l-4 4"/><circle cx="10" cy="14" r="2"/></svg>,
  Schedule: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><line x1="9" y1="15" x2="15" y2="15"/></svg>,
  MessageCircle: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>,
  Mic: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>,
  Send: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
};

const CATEGORIES = [
  { title: "Open Days", desc: "Explore our campus and meet faculty at upcoming open days.", icon: Icons.Calendar, color: "var(--accent-teal)" },
  { title: "Live & Camp", desc: "Experience campus life through live events and camp programmes.", icon: Icons.Camp, color: "var(--accent-orange)" },
  { title: "Accommodation", desc: "Find your perfect on-campus or nearby housing options.", icon: Icons.Home, color: "var(--accent-purple)" },
  { title: "Undergraduate Courses", desc: "Browse our full range of undergraduate degree programmes.", icon: Icons.Mortarboard, color: "var(--accent-blue)" },
  { title: "Events", desc: "Stay updated on workshops, seminars, and social events.", icon: Icons.Party, color: "var(--accent-yellow)" },
  { title: "School Calendar", desc: "View important dates, terms, and academic deadlines.", icon: Icons.Schedule, color: "var(--accent-pink)" }
];

function App() {
  const [messages, setMessages] = useState([
    {
      role: 'ai',
      text: "Hi there! 👋 I'm ChariotAI, your AI Powered Student Support Chatbot. I can help you with information about open days, accommodation, courses, events, and more. How can I help you today?",
      sources: []
    }
  ]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const chatEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // Auto scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-GB';

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        setIsRecording(false);
      };

      recognitionRef.current.onerror = () => {
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }
  }, []);

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      alert('Voice input is not supported in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      recognitionRef.current.start();
      setIsRecording(true);
    }
  };

  const handleSend = async () => {
    if (!inputText.trim()) return;
    
    const userMsg = inputText.trim();
    setMessages(prev => [...prev, { role: 'human', text: userMsg }]);
    setInputText("");
    setIsLoading(true);

    // Build conversation history (excluding the very first welcome message if preferred, or just tail 6)
    const apiHistory = messages.slice(-6).map(m => ({
      role: m.role,
      text: m.text
    }));

    try {
      const apiUrl = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";
      
      // Add timeout to detect slow responses
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      const response = await fetch(`${apiUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg, history: apiHistory }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'ai', text: data.answer, sources: data.sources }]);
      
      // Feature 4: Live Human Handoff simulation
      if (data.handoff_required) {
        setTimeout(() => {
          setMessages(prev => [...prev, { 
            role: 'ai', 
            text: "🔄 **Live Agent Handoff Triggered.** Routing your session to the next available Support Staff member... Please hold.", 
            sources: [] 
          }]);
        }, 1500);
      }
    } catch (error) {
      let errorMsg = "Sorry, I am having trouble connecting to the server.";
      if (error.name === 'AbortError') {
        errorMsg = "⏱️ The request is taking longer than expected. The server might be warming up (Azure cold start). Please try again in a moment.";
      } else if (error.message.includes('500')) {
        errorMsg = "🔧 The server encountered an error. Please try rephrasing your question or try again shortly.";
      }
      setMessages(prev => [...prev, { role: 'ai', text: errorMsg, sources: [] }]);
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <>
      <main>
        {/* Banner Section */}
        <section className="hero-banner">
          <h1>🤖 ChariotAI - AI Powered Student Support Chatbot</h1>
          <p>Your inclusive AI assistant for campus life</p>
        </section>

        {/* Main Interface */}
        <div className="main-container">
          <h2>How can I help you?</h2>
          
          <div className="categories-grid">
            {CATEGORIES.map((cat, idx) => (
              <div 
                key={idx} 
                className="category-card"
                style={{ animationFillMode: 'both', animationDelay: `${idx * 0.08}s` }}
                onClick={() => setInputText(`Tell me about ${cat.title}`)}
              >
                <div className="icon-wrapper" style={{ backgroundColor: cat.color }}>
                  {cat.icon}
                </div>
                <h3>{cat.title}</h3>
                <p>{cat.desc}</p>
              </div>
            ))}
          </div>

          {/* Chat Interface */}
          <div className="chat-container">
            <div className="chat-header">
              <div className="chat-header-left">
                {Icons.MessageCircle} Chat with an Agent
              </div>
              <div className="online-dot" title="Online"></div>
            </div>

            <div className="chat-history">
              {messages.map((msg, idx) => (
                <div key={idx} className={`message-wrapper ${msg.role}`}>
                  <div className="avatar">
                    {msg.role === 'ai' ? '🤖' : '👩‍🎓'}
                  </div>
                  <div className="message-content">
                    <div className="message-bubble">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.text}
                      </ReactMarkdown>
                    </div>
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="sources-container">
                        <strong>Sources:</strong>
                        <ul>
                          {msg.sources.map((src, i) => (
                            <li key={i}><a href={src} target="_blank" rel="noopener noreferrer">{src}</a></li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message-wrapper ai">
                  <div className="avatar">🤖</div>
                  <div className="typing-indicator">ChariotAI is typing...</div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <div className="chat-input-area">
              <div className="chat-input-wrapper">
                <input
                  type="text"
                  placeholder="Type your question here..."
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyUp={handleKeyPress}
                  disabled={isLoading}
                />
                <div className="input-actions">
                  <button 
                    className={`icon-button ${isRecording ? 'recording' : ''}`}
                    onClick={toggleVoiceInput}
                    title={isRecording ? "Stop Recording" : "Voice Input"}
                    disabled={isLoading}
                  >
                    {Icons.Mic}
                  </button>
                </div>
              </div>
              <button 
                className="icon-button send-button" 
                onClick={handleSend}
                disabled={isLoading || !inputText.trim()}
              >
                {Icons.Send}
              </button>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}

export default App;
