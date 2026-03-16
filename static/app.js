const { useState, useEffect, useRef } = React;

const API_BASE = "";

function App() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [sessionId, setSessionId] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState(null);
    const [pdfUploaded, setPdfUploaded] = useState(false);
    const [pdfName, setPdfName] = useState(null);
    const [lastDomain, setLastDomain] = useState(null);
    const [stats, setStats] = useState({
        queries: 0,
        citations: 0,
        avgTime: 0
    });
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setUploadStatus({ type: "loading", message: "Uploading and processing PDF..." });

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch(`${API_BASE}/api/v1/documents/upload`, {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                setPdfUploaded(true);
                setPdfName(file.name);
                setUploadStatus({
                    type: "success",
                    message: `${file.name} ready! ${data.chunks_created} chunks created.`
                });
                setMessages(prev => [...prev, {
                    role: "bot",
                    content: `I have successfully processed **${file.name}**. I created ${data.chunks_created} searchable chunks from your document.\n\nYou can now ask me anything about this document, and I will also cross-reference with Indian law!`,
                    domain: null,
                    responseTime: null
                }]);
            } else {
                setUploadStatus({
                    type: "error",
                    message: data.detail || "Upload failed"
                });
            }
        } catch (error) {
            setUploadStatus({
                type: "error",
                message: "Upload failed. Please try again."
            });
        }
    };

    const sendMessage = async (questionText = null) => {
        const question = questionText || input.trim();
        if (!question || isLoading) return;

        setInput("");
        setIsLoading(true);

        setMessages(prev => [...prev, {
            role: "user",
            content: question
        }]);

        try {
            const response = await fetch(`${API_BASE}/api/v1/chat/query`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question: question,
                    session_id: sessionId
                })
            });

            const data = await response.json();

            if (response.ok) {
                if (!sessionId) setSessionId(data.session_id);
                setLastDomain(data.legal_domain);

                setStats(prev => ({
                    queries: prev.queries + 1,
                    citations: prev.citations + (data.citations?.length || 0),
                    avgTime: prev.queries === 0
                        ? data.response_time_ms || 0
                        : Math.round(
                            (prev.avgTime * prev.queries + (data.response_time_ms || 0))
                            / (prev.queries + 1)
                        )
                }));

                setMessages(prev => [...prev, {
                    role: "bot",
                    content: data.answer,
                    domain: data.legal_domain,
                    responseTime: data.response_time_ms,
                    citations: data.citations
                }]);
            } else {
                setMessages(prev => [...prev, {
                    role: "bot",
                    content: "Sorry, something went wrong. Please try again.",
                    domain: null,
                    responseTime: null
                }]);
            }
        } catch (error) {
            setMessages(prev => [...prev, {
                role: "bot",
                content: "Connection error. Please check if the server is running.",
                domain: null,
                responseTime: null
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const clearChat = async () => {
        if (sessionId) {
            await fetch(`${API_BASE}/api/v1/chat/clear`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: sessionId })
            });
        }
        setMessages([]);
        setSessionId(null);
        setPdfUploaded(false);
        setPdfName(null);
        setUploadStatus(null);
        setLastDomain(null);
        setStats({ queries: 0, citations: 0, avgTime: 0 });
    };

    const handleKeyPress = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const exampleQueries = [
        "A police officer is being rude to me. What are my legal rights?",
        "My landlord refuses to return my security deposit. What can I do?",
        "My employer fired me without notice. What are my rights?",
        "Someone has encroached on my land. How do I approach the court?"
    ];

    return (
        <div style={{display: "flex", flexDirection: "column", height: "100vh"}}>
            {/* Header */}
            <div className="header">
                <div className="header-left">
                    <div>
                        <h1>⚖️ Enterprise Legal Counsel AI</h1>
                        <p>Powered by Multi-Agent RAG • LLaMA 3 • LangChain • LangGraph</p>
                    </div>
                </div>
                <span className="status-badge">● Live</span>
            </div>

            {/* Main */}
            <div className="main">
                {/* Left Panel */}
                <div className="left-panel">
                    {/* Upload */}
                    <div>
                        <div className="panel-title">Legal Document</div>
                        <div
                            className={`upload-area ${pdfUploaded ? "uploaded" : ""}`}
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <div className="upload-icon">
                                {pdfUploaded ? "📄" : "📁"}
                            </div>
                            <div className="upload-text">
                                <strong>
                                    {pdfUploaded ? pdfName : "Upload PDF (Optional)"}
                                </strong>
                                {!pdfUploaded && "Click to upload legal document"}
                                {pdfUploaded && "Click to upload different document"}
                            </div>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept=".pdf"
                                onChange={handleFileUpload}
                                style={{display: "none"}}
                            />
                        </div>
                        {uploadStatus && (
                            <div className={`upload-status ${uploadStatus.type}`}>
                                {uploadStatus.message}
                            </div>
                        )}
                    </div>

                    {/* Mode */}
                    <div>
                        <div className="panel-title">Current Mode</div>
                        <div className="mode-card">
                            <div className="mode-title">Active Mode</div>
                            <div className="mode-value">
                                {pdfUploaded ? "Document + Law Mode" : "Indian Law Mode"}
                            </div>
                            {lastDomain && (
                                <span className="domain-badge">{lastDomain}</span>
                            )}
                        </div>
                    </div>

                    {/* Stats */}
                    <div>
                        <div className="panel-title">Session Stats</div>
                        <div className="stats-grid">
                            <div className="stat-card">
                                <div className="stat-value">{stats.queries}</div>
                                <div className="stat-label">Queries</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-value">{stats.citations}</div>
                                <div className="stat-label">Citations</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-value">{stats.avgTime}</div>
                                <div className="stat-label">Avg ms</div>
                            </div>
                            <div className="stat-card">
                                <div className="stat-value">
                                    {sessionId ? sessionId.slice(0,4) : "--"}
                                </div>
                                <div className="stat-label">Session</div>
                            </div>
                        </div>
                    </div>

                    {/* Clear */}
                    <button className="btn-clear" onClick={clearChat}>
                        🗑️ Clear Chat & Reset
                    </button>
                </div>

                {/* Chat Panel */}
                <div className="chat-panel">
                    <div className="chat-messages">
                        {messages.length === 0 ? (
                            <div className="welcome-message">
                                <h2>⚖️ Welcome to Legal Counsel AI</h2>
                                <p>
                                    Your AI-powered Indian Legal Assistant.
                                    Ask any legal question or upload a legal
                                    document for detailed analysis.
                                </p>
                                <div className="example-queries">
                                    {exampleQueries.map((q, i) => (
                                        <button
                                            key={i}
                                            className="example-query"
                                            onClick={() => sendMessage(q)}
                                        >
                                            {q}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            messages.map((msg, i) => (
                                <div key={i} className={`message ${msg.role}`}>
                                    <div className="message-avatar">
                                        {msg.role === "user" ? "👤" : "⚖️"}
                                    </div>
                                    <div>
                                        <div
                                            className="message-content"
                                            dangerouslySetInnerHTML={{
                                                __html: marked.parse(msg.content || "")
                                            }}
                                        />
                                        {msg.role === "bot" && (
                                            <div className="message-meta">
                                                {msg.domain && (
                                                    <span className="meta-badge">
                                                        {msg.domain}
                                                    </span>
                                                )}
                                                {msg.responseTime && (
                                                    <span className="meta-badge">
                                                        {Math.round(msg.responseTime)}ms
                                                    </span>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}
                        {isLoading && (
                            <div className="message bot">
                                <div className="message-avatar">⚖️</div>
                                <div className="typing-indicator">
                                    <div className="typing-dot"></div>
                                    <div className="typing-dot"></div>
                                    <div className="typing-dot"></div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="input-area">
                        <div className="input-wrapper">
                            <textarea
                                className="input-box"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Ask any legal question..."
                                rows={1}
                                disabled={isLoading}
                            />
                            <button
                                className="btn-send"
                                onClick={() => sendMessage()}
                                disabled={isLoading || !input.trim()}
                            >
                                {isLoading ? "Thinking..." : "Ask ⚖️"}
                            </button>
                        </div>
                        <div className="input-hint">
                            Press Enter to send • Shift+Enter for new line
                        </div>
                    </div>

                    {/* Disclaimer */}
                    <div className="disclaimer">
                        ⚠️ AI-generated legal information for educational
                        purposes only. Not legal advice.
                    </div>
                </div>
            </div>
        </div>
    );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
