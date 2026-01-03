import { useState, useEffect } from 'react';
import axios from 'axios';
import { Clock, Activity, Zap } from 'lucide-react';

const API_URL = 'http://127.0.0.1:8000/api';

function ChecksHistory({ gatewayName }) {
  const [checks, setChecks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const fetchChecks = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/gateways/${gatewayName}/checks?limit=10`);
      setChecks(response.data);
    } catch (err) {
      console.error('Error fetching checks:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isExpanded && checks.length === 0) {
      fetchChecks();
    }
  }, [isExpanded]);

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-CL', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getStatusEmoji = (status) => {
    const statusMap = {
      'OPERATIONAL': '✅',
      'DEGRADED': '⚠️',
      'PARTIAL_OUTAGE': '🟠',
      'MAJOR_OUTAGE': '🔴',
      'DOWN': '❌'
    };
    return statusMap[status] || '❓';
  };

  return (
    <div className="checks-history">
      <button 
        className="toggle-history"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {isExpanded ? '▲' : '▼'} Ver Histórico de Checks
      </button>

      {isExpanded && (
        <div className="history-list">
          {loading ? (
            <p className="loading-checks">Cargando...</p>
          ) : checks.length === 0 ? (
            <p className="no-checks">No hay checks disponibles</p>
          ) : (
            checks.map((check) => (
              <div key={check.id} className="check-item">
                <div className="check-time">
                  <Clock size={14} />
                  {formatTime(check.timestamp)}
                </div>
                <div className="check-status">
                  <Activity size={14} />
                  {getStatusEmoji(check.status)} {check.status}
                </div>
                {check.response_time && (
                  <div className="check-response">
                    <Zap size={14} />
                    {check.response_time}ms
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default ChecksHistory;