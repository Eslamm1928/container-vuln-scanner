import React, { useState, useEffect } from 'react';
import './App.css';
import ScanList from './components/ScanList';
import ScanForm from './components/ScanForm';
import VulnerabilityList from './components/VulnerabilityList';
import { getScans, submitScan, getVulnerabilities } from './services/api';

function App() {
  const [scans, setScans] = useState([]);
  const [selectedScan, setSelectedScan] = useState(null);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // التعديل 1: تثبيت الرابط ليشير إلى NodePort الصحيح
  const API_URL = 'http://172.19.0.2:31585';

  useEffect(() => {
    loadScans();
    // Auto-refresh every 5 seconds
    const interval = setInterval(loadScans, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedScan) {
      loadVulnerabilities(selectedScan);
    }
  }, [selectedScan]);

  const loadScans = async () => {
    try {
      setRefreshing(true);
      const data = await getScans(API_URL);
      setScans(data);
      setError(null);
    } catch (err) {
      setError('Failed to load scans. Make sure the API is running.');
      console.error('Error loading scans:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const loadVulnerabilities = async (scanId) => {
    try {
      const data = await getVulnerabilities(API_URL, scanId);
      setVulnerabilities(data);
    } catch (err) {
      console.error('Error loading vulnerabilities:', err);
      setVulnerabilities([]);
    }
  };

  const handleSubmitScan = async (imageName) => {
    try {
      const result = await submitScan(API_URL, imageName);
      await loadScans();
      return result;
    } catch (err) {
      throw err;
    }
  };

  const handleScanClick = (scan) => {
    // التعديل 2: استخدام id بدلاً من scan_id ليتوافق مع الـ API الجديد
    if (selectedScan === scan.id) {
      setSelectedScan(null);
      setVulnerabilities([]);
    } else {
      setSelectedScan(scan.id);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔒 Container Vulnerability Scanner</h1>
        <p>Monitor and scan container images for security vulnerabilities</p>
      </header>

      <div className="container">
        {error && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
            <button onClick={loadScans}>Retry</button>
          </div>
        )}

        <div className="main-content">
          <div className="left-panel">
            <ScanForm onSubmit={handleSubmitScan} />
            
            <div className="scans-section">
              <div className="section-header">
                <h2>Scans</h2>
                <button 
                  className="refresh-btn" 
                  onClick={loadScans}
                  disabled={refreshing}
                >
                  {refreshing ? '🔄' : '↻'} Refresh
                </button>
              </div>
              
              {loading ? (
                <div className="loading">Loading scans...</div>
              ) : (
                <ScanList 
                  scans={scans} 
                  selectedScan={selectedScan}
                  onScanClick={handleScanClick}
                />
              )}
            </div>
          </div>

          <div className="right-panel">
            {selectedScan && (
              <VulnerabilityList 
                scanId={selectedScan}
                vulnerabilities={vulnerabilities}
                onClose={() => {
                  setSelectedScan(null);
                  setVulnerabilities([]);
                }}
              />
            )}
            {!selectedScan && (
              <div className="empty-state">
                <p>👆 Select a scan to view vulnerabilities</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
