import React, { useState } from 'react';
import './ScanForm.css';

function ScanForm({ onSubmit }) {
  const [imageName, setImageName] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!imageName.trim()) {
      setMessage({ type: 'error', text: 'Please enter an image name' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const result = await onSubmit(imageName.trim());
      setMessage({ 
        type: 'success', 
        text: `Scan queued successfully! Scan ID: ${result.scan_id}` 
      });
      setImageName('');
    } catch (err) {
      setMessage({ 
        type: 'error', 
        text: err.response?.data?.detail || 'Failed to submit scan' 
      });
    } finally {
      setLoading(false);
      setTimeout(() => setMessage(null), 5000);
    }
  };

  return (
    <div className="scan-form">
      <h2>Submit New Scan</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="imageName">Container Image Name:</label>
          <input
            id="imageName"
            type="text"
            value={imageName}
            onChange={(e) => setImageName(e.target.value)}
            placeholder="e.g., nginx, redis, postgres"
            disabled={loading}
          />
        </div>
        <button type="submit" disabled={loading || !imageName.trim()}>
          {loading ? '⏳ Submitting...' : '🚀 Start Scan'}
        </button>
        {message && (
          <div className={`message ${message.type}`}>
            {message.type === 'success' ? '✅' : '❌'} {message.text}
          </div>
        )}
      </form>
    </div>
  );
}

export default ScanForm;




