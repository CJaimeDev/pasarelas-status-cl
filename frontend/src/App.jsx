import { useState, useEffect } from 'react';
import axios from 'axios';
import { Moon, Sun, RefreshCw } from 'lucide-react';
import GatewayCard from './components/GatewayCard';
import './App.css';

const API_URL = 'http://127.0.0.1:8000/api';

function App() {
  const [gateways, setGateways] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [darkMode, setDarkMode] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchStatus = async () => {
    try {
      setIsRefreshing(true);
      const response = await axios.get(`${API_URL}/status`);
      setGateways(response.data);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError('Error al conectar con el servidor');
      console.error('Error fetching status:', err);
    } finally {
      setLoading(false);
      setTimeout(() => setIsRefreshing(false), 500);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [darkMode]);

  return (
    <div className={`app ${darkMode ? 'dark' : ''}`}>
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>🇨🇱 Monitor de Pasarelas de Pago Chile</h1>
            <p className="subtitle">
              Monitoreo en tiempo real de las principales pasarelas de pago chilenas
            </p>
          </div>
          
          <div className="header-actions">
            <button 
              className="refresh-btn"
              onClick={fetchStatus}
              disabled={isRefreshing}
            >
              <RefreshCw size={20} className={isRefreshing ? 'spinning' : ''} />
              Actualizar
            </button>
            
            <button 
              className="theme-toggle"
              onClick={() => setDarkMode(!darkMode)}
              aria-label="Toggle dark mode"
            >
              {darkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
          </div>
        </div>
        
        {lastUpdate && (
          <p className="last-update">
            Última actualización: {lastUpdate.toLocaleTimeString('es-CL')}
          </p>
        )}
      </header>

      <main className="app-main">
        {loading && gateways.length === 0 ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Cargando...</p>
          </div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : (
          <div className="gateways-grid">
            {gateways.map((item) => (
              <GatewayCard
                key={item.gateway.id}
                gateway={item.gateway}
                lastCheck={item.last_check}
                uptime24h={item.uptime_24h}
              />
            ))}
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Proyecto de portfolio - Monitoreo vía APIs oficiales de status
        </p>
      </footer>
    </div>
  );
}

export default App;