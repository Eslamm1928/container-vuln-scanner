import React from 'react';
import './ScanList.css';

function ScanList({ scans, selectedScan, onScanClick }) {
  const getStatusBadge = (status) => {
    const statusConfig = {
      PENDING: { class: 'pending', icon: '⏳', color: '#ffa500' },
      RUNNING: { class: 'running', icon: '🔄', color: '#2196F3' },
      DONE: { class: 'done', icon: '✅', color: '#4CAF50' },
      FAILED: { class: 'failed', icon: '❌', color: '#f44336' }
    };

    const config = statusConfig[status] || { class: 'unknown', icon: '❓', color: '#999' };
    
    return (
      <span className={`status-badge ${config.class}`} style={{ backgroundColor: config.color }}>
        {config.icon} {status}
      </span>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  if (scans.length === 0) {
    return (
      <div className="empty-scans">
        <p>No scans yet. Submit a scan to get started!</p>
      </div>
    );
  }

  return (
    <div className="scan-list">
      {scans.map((scan) => (
        <div
          // التعديل 1: المفتاح الأساسي مضبوط بالفعل
          key={scan.id} 
          // التعديل 2: تغيير scan_id إلى id
          className={`scan-item ${selectedScan === scan.id ? 'selected' : ''}`}
          onClick={() => onScanClick(scan)}
        >
          <div className="scan-header">
            {/* التعديل 3: تغيير scan_id إلى id ليظهر الرقم بجانب الهاشتاج */}
            <div className="scan-id">#{scan.id}</div>
            {getStatusBadge(scan.status)}
          </div>
          <div className="scan-details">
            <div className="scan-image">
              {/* التعديل 4: تغيير image إلى image_name */}
              <strong>📦 {scan.image_name}</strong>
            </div>
            <div className="scan-date">
              {/* التعديل 5: تغيير created_at إلى scan_date */}
              🕒 {formatDate(scan.scan_date)}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default ScanList;
