import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';


function App() {
  const [step, setStep] = useState(1); // 1: Upload, 2: Transcript, 3: Extraction, 4: Final
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [audioFile, setAudioFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const [rawTranscript, setRawTranscript] = useState('');
  const [segments, setSegments] = useState([]);
  const [refinedTranscript, setRefinedTranscript] = useState('');
  const [extractedData, setExtractedData] = useState({});
  const [templateDetails, setTemplateDetails] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState('');

  // Recorder State
  const [isRecordingMode, setIsRecordingMode] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [timerInterval, setTimerInterval] = useState(null);

  // Chat State
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  // Recording Logic
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = e => chunks.push(e.data);
      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        const file = new File([blob], "recording.webm", { type: 'audio/webm' });
        setAudioFile(file);
        stream.getTracks().forEach(track => track.stop()); // Stop mic access
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
      setRecordingTime(0);

      const interval = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      setTimerInterval(interval);

    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("Microphone access denied or not available.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
      setIsRecording(false);
      clearInterval(timerInterval);
    }
  };



  useEffect(() => {
    fetch(`${API_BASE}/templates`)
      .then(res => res.json())
      .then(data => setTemplates(data));
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!audioFile || !selectedTemplate) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('audio', audioFile);
    formData.append('body_part_id', selectedTemplate);

    try {
      const res = await fetch(`${API_BASE}/transcribe`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setRawTranscript(data.raw_transcript);
      setSegments(data.segments);
      setRefinedTranscript(data.refined_transcript);
      setExtractedData(data.extracted_data);

      // Fetch details for rendering the form
      const templateRes = await fetch(`${API_BASE}/template/${data.template_id}.json`);
      const templateData = await templateRes.json();
      setTemplateDetails(templateData);

      setStep(2);
    } catch (err) {
      console.error(err);
      alert("Error processing audio. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyTranscript = () => {
    setStep(3);
  };

  const handleVerifyExtraction = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/generate-report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: extractedData, template_id: selectedTemplate }),
      });
      const data = await res.json();
      setDownloadUrl(data.download_url);
      setStep(4);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMessage = { role: 'user', content: chatInput };
    setChatMessages([...chatMessages, userMessage]);
    setChatInput('');
    setChatLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: chatInput,
          transcript: refinedTranscript,
          body_part: templateDetails?.organ || '',
          template_id: selectedTemplate,
          history: chatMessages
        }),
      });
      const data = await res.json();
      setChatMessages(prev => [...prev, { role: 'ai', content: data.response }]);
    } catch (err) {
      console.error(err);
      setChatMessages(prev => [...prev, { role: 'ai', content: "Error communicating with Assistant." }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleRestart = () => {
    setStep(1);
    setAudioFile(null);
    setSelectedTemplate('');
    setDownloadUrl('');
    setChatMessages([]);
  };

  return (
    <div className="dashboard">
      <div className="sidebar">
        <div>
          <h2>TURO-AI</h2>
          <p style={{ opacity: 0.7, fontSize: '0.8rem' }}>Hyper-Accuracy Engine</p>
        </div>

        <nav style={{ marginTop: '2rem' }}>
          <div className={`nav-item ${step === 1 ? 'active' : ''}`}>1. Initial Intake</div>
          <div className={`nav-item ${step === 2 ? 'active' : ''}`}>2. Transcription</div>
          <div className={`nav-item ${step === 3 ? 'active' : ''}`}>3. Verification</div>
          <div className={`nav-item ${step === 4 ? 'active' : ''}`}>4. Final Report</div>
        </nav>
      </div>

      <main className="main-content">
        {loading && (
          <div className="loader-overlay">
            <div className="loader"></div>
            <p>Processing with LangGraph Engine...</p>
          </div>
        )}

        {step === 1 && (
          <div className="step-container">
            <h1 style={{ marginBottom: '2rem' }}>Radiology Case Upload</h1>
            <Card title="Patient & Exam Context">
              <div className="form-group">
                <label>Target Organ / Body Part</label>
                <select
                  value={selectedTemplate}
                  onChange={(e) => setSelectedTemplate(e.target.value)}
                  className="select-input"
                >
                  <option value="">Select a protocol...</option>
                  {templates.map(t => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Input Method</label>
                <div className="toggle-group" style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                  <button
                    className={`btn ${!isRecordingMode ? 'btn-primary' : ''}`}
                    onClick={() => setIsRecordingMode(false)}
                    style={{ flex: 1, border: '1px solid var(--border)' }}
                  >
                    📁 File Upload
                  </button>
                  <button
                    className={`btn ${isRecordingMode ? 'btn-primary' : ''}`}
                    onClick={() => setIsRecordingMode(true)}
                    style={{ flex: 1, border: '1px solid var(--border)' }}
                  >
                    🎙️ Record Voice
                  </button>
                </div>

                {isRecordingMode ? (
                  <div className="recorder-zone" style={{ textAlign: 'center', padding: '2rem', border: '2px dashed var(--border)', borderRadius: 'var(--radius)' }}>
                    {!isRecording ? (
                      <button
                        className="btn btn-danger"
                        onClick={startRecording}
                        style={{ fontSize: '1.2rem', padding: '1rem 2rem', background: '#dc3545', color: 'white', border: 'none', borderRadius: '50px' }}
                      >
                        🔴 Start Recording
                      </button>
                    ) : (
                      <div className="recording-active">
                        <div className="pulse-ring" style={{ width: '60px', height: '60px', background: '#dc3545', borderRadius: '50%', margin: '0 auto 1rem', animation: 'pulse 1.5s infinite' }}></div>
                        <p style={{ color: '#dc3545', fontWeight: 'bold' }}>Recording... {recordingTime}s</p>
                        <button
                          className="btn"
                          onClick={stopRecording}
                          style={{ marginTop: '1rem', border: '1px solid var(--border)' }}
                        >
                          ⏹️ Stop & Use This
                        </button>
                      </div>
                    )}

                    {audioFile && (
                      <div style={{ marginTop: '1rem', padding: '0.5rem', background: '#e9ecef', borderRadius: 'var(--radius)' }}>
                        <p>✅ Audio Captured ({audioFile.size ? (audioFile.size / 1024 / 1024).toFixed(2) : 0} MB)</p>
                        <audio controls src={URL.createObjectURL(audioFile)} style={{ marginTop: '0.5rem', width: '100%' }} />
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="upload-zone" onClick={() => document.getElementById('audio-upload').click()}>
                    {audioFile ? (
                      <p>✅ {audioFile.name} selected</p>
                    ) : (
                      <p>Drop radiology recording here or click to browse</p>
                    )}
                    <input
                      id="audio-upload"
                      type="file"
                      hidden
                      accept="audio/*"
                      onChange={(e) => setAudioFile(e.target.files[0])}
                    />
                  </div>
                )}
              </div>

              <button
                className="btn btn-primary"
                onClick={handleUpload}
                disabled={!audioFile || !selectedTemplate}
              >
                Commence Processing
              </button>
            </Card>
          </div>
        )}

        {step === 2 && (
          <div className="step-container">
            <h1 style={{ marginBottom: '2rem' }}>Medical Transcription & Refinement</h1>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
              <Card title="Raw Segments (with Timestamps)">
                <div className="segments-list" style={{ maxHeight: '500px', overflowY: 'auto', padding: '1rem', background: '#f8f9fa', borderRadius: 'var(--radius)' }}>
                  {segments.map((s, i) => (
                    <div key={i} className="segment-item" style={{ marginBottom: '1rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border)' }}>
                      <span className="timestamp" style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--primary)', display: 'block' }}>
                        [{s.start.toFixed(2)}s - {s.end.toFixed(2)}s]
                      </span>
                      <p style={{ fontSize: '0.9rem' }}>{s.text}</p>
                    </div>
                  ))}
                </div>
              </Card>

              <Card title="AI Refined & Verified Transcript">
                <label style={{ fontSize: '0.8rem', opacity: 0.7, marginBottom: '0.5rem', display: 'block' }}>
                  Verify spelling and context according to {selectedTemplate.split('_')[0]} vocabulary.
                </label>
                <textarea
                  value={refinedTranscript}
                  onChange={(e) => setRefinedTranscript(e.target.value)}
                  rows={15}
                  className="textarea-input"
                  style={{ width: '100%', padding: '1rem', border: '1px solid var(--border)', borderRadius: 'var(--radius)', fontFamily: 'Inter, sans-serif' }}
                />
                <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem' }}>
                  <button className="btn btn-primary" onClick={handleVerifyTranscript}>Confirm Review</button>
                  <button className="btn" onClick={() => setStep(1)} style={{ border: '1px solid var(--border)' }}>Back</button>
                </div>
              </Card>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="step-container">
            <h1 style={{ marginBottom: '1rem' }}>Final Clinical Approval</h1>
            <p style={{ marginBottom: '2rem', color: 'var(--text-muted)' }}>
              Review the extracted information below. These fields will be used to generate the final DOCX report.
              Edit any field if necessary before clicking <b>Approve & Generate Report</b>.
            </p>

            <div className="form-container" style={{ background: '#fff', padding: '2rem', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
              {templateDetails?.sections.map((section, idx) => (
                <div key={idx} className="form-section" style={{ marginBottom: '2.5rem' }}>
                  <h3 style={{ borderBottom: '2px solid var(--primary)', paddingBottom: '0.5rem', marginBottom: '1.5rem', fontSize: '1.1rem', color: 'var(--primary)' }}>
                    {section.name}
                  </h3>
                  <div className="fields-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    {section.fields.map((field) => (
                      <div key={field.field_id} className="field-group">
                        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem' }}>{field.label}</label>
                        {field.type === 'select' ? (
                          <select
                            value={extractedData[field.field_id] || ''}
                            onChange={(e) => setExtractedData({ ...extractedData, [field.field_id]: e.target.value })}
                            className="select-input"
                            style={{ width: '100%' }}
                          >
                            <option value="">not determined</option>
                            {field.options.map(opt => (
                              <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                          </select>
                        ) : (
                          <input
                            type="text"
                            value={extractedData[field.field_id] || ''}
                            onChange={(e) => setExtractedData({ ...extractedData, [field.field_id]: e.target.value })}
                            className="input-field"
                            placeholder="Enter findings..."
                            style={{ width: '100%' }}
                          />
                        )}
                        {!extractedData[field.field_id] && (
                          <span style={{ fontSize: '0.7rem', color: '#666', marginTop: '0.25rem', display: 'block', fontStyle: 'italic' }}>
                            Marked as "not determined" in final report
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}

              <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', borderTop: '1px solid var(--border)', paddingTop: '2rem' }}>
                <button
                  className="btn btn-primary"
                  onClick={handleVerifyExtraction}
                  style={{ padding: '0.8rem 2rem', fontSize: '1rem' }}
                >
                  Approve & Generate Report
                </button>
                <button className="btn" onClick={() => setStep(2)} style={{ border: '1px solid var(--border)' }}>Back to Transcription</button>
              </div>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="step-container" style={{ textAlign: 'center', padding: '4rem 0' }}>
            <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📄</div>
            <h1>Report Generated Successfully</h1>
            <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
              The final CAP-compliant document is ready for download.
            </p>

            <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
              <a
                href={`${API_BASE}${downloadUrl}`}
                target="_blank"
                rel="noreferrer"
                className="btn btn-primary"
                style={{ textDecoration: 'none' }}
              >
                Download DOCX
              </a>
              <button className="btn" onClick={handleRestart} style={{ border: '1px solid var(--border)' }}>New Case</button>
            </div>
          </div>
        )}

        {step === 3 && (
          <>
            {isChatOpen ? (
              <div className="chat-window">
                <div className="chat-header">
                  <span>Assistant</span>
                  <button onClick={() => setIsChatOpen(false)} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', fontSize: '1.2rem' }}>×</button>
                </div>
                <div className="chat-body">
                  {chatMessages.length === 0 && (
                    <div className="chat-message message-ai">
                      Hello! I have analyzed the transcript. Ask me anything about the findings or the protocol.
                    </div>
                  )}
                  {chatMessages.map((msg, i) => (
                    <div key={i} className={`chat-message ${msg.role === 'user' ? 'message-user' : 'message-ai'}`}>
                      {msg.content}
                    </div>
                  ))}
                  {chatLoading && <div className="chat-message message-ai">Analyzing transcript...</div>}
                </div>
                <form className="chat-footer" onSubmit={handleSendMessage}>
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask about findings..."
                    autoFocus
                  />
                  <button type="submit" className="btn btn-primary" disabled={chatLoading}>Send</button>
                </form>
              </div>
            ) : (
              <div className="chat-toggle" onClick={() => setIsChatOpen(true)}>
                💬
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

function Card({ title, children }) {
  return (
    <div className="card">
      <h2 className="card-title">{title}</h2>
      {children}
    </div>
  );
}

export default App;
