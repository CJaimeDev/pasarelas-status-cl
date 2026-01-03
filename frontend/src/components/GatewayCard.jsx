import UptimeChart from './UptimeChart';
import ChecksHistory from './ChecksHistory';

function GatewayCard({ gateway, lastCheck, uptime24h }) {
  const getStatusDisplay = (status) => {
    const statusMap = {
      'OPERATIONAL': { emoji: '✅', color: '#22c55e', text: 'Operacional' },
      'DEGRADED': { emoji: '⚠️', color: '#f59e0b', text: 'Degradado' },
      'PARTIAL_OUTAGE': { emoji: '🟠', color: '#ef4444', text: 'Caída Parcial' },
      'MAJOR_OUTAGE': { emoji: '🔴', color: '#dc2626', text: 'Caída Mayor' },
      'DOWN': { emoji: '❌', color: '#991b1b', text: 'Caído' }
    };
    return statusMap[status] || { emoji: '❓', color: '#6b7280', text: 'Desconocido' };
  };

  const statusDisplay = lastCheck 
    ? getStatusDisplay(lastCheck.status) 
    : { emoji: '⏳', color: '#6b7280', text: 'Sin datos' };

  const getTimeSince = (timestamp) => {
    if (!timestamp) return 'Sin datos';
    const now = new Date();
    const checkTime = new Date(timestamp);
    const diffMs = now - checkTime;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Hace menos de 1 min';
    if (diffMins === 1) return 'Hace 1 minuto';
    if (diffMins < 60) return `Hace ${diffMins} minutos`;
    
    const diffHours = Math.floor(diffMins / 60);
    return diffHours === 1 ? 'Hace 1 hora' : `Hace ${diffHours} horas`;
  };

  return (
    <div className="gateway-card">
      <div className="gateway-header">
        <h3>{gateway.display_name}</h3>
        <span className="status-badge" style={{ backgroundColor: statusDisplay.color }}>
          {statusDisplay.emoji} {statusDisplay.text}
        </span>
      </div>
      
      <div className="gateway-stats">
        <div className="stat">
          <span className="stat-label">Uptime 24h:</span>
          <span className="stat-value">
            {uptime24h !== null ? `${uptime24h}%` : 'N/A'}
          </span>
        </div>
        
        <div className="stat">
          <span className="stat-label">Último check:</span>
          <span className="stat-value time-indicator">
            {getTimeSince(lastCheck?.timestamp)}
          </span>
        </div>
        
        {lastCheck?.response_time && (
          <div className="stat">
            <span className="stat-label">Tiempo respuesta:</span>
            <span className="stat-value">{lastCheck.response_time}ms</span>
          </div>
        )}
      </div>

      <UptimeChart gatewayName={gateway.name} />
      
      <ChecksHistory gatewayName={gateway.name} />
    </div>
  );
}

export default GatewayCard;