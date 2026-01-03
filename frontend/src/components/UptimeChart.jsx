import { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const API_URL = 'http://127.0.0.1:8000/api';

function UptimeChart({ gatewayName }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUptimeData = async () => {
      try {
        const response = await axios.get(`${API_URL}/gateways/${gatewayName}/uptime/days?days=7`);
        setData(response.data);
      } catch (err) {
        console.error('Error fetching uptime data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchUptimeData();
  }, [gatewayName]);

  // Filtrar días sin datos para el gráfico
  const chartData = data.filter(d => d.uptime !== null);

  if (loading) {
    return (
      <div className="uptime-chart">
        <h4>Uptime últimos 7 días</h4>
        <p style={{ textAlign: 'center', color: '#6b7280', padding: '2rem' }}>
          Cargando...
        </p>
      </div>
    );
  }

  if (chartData.length === 0) {
    return (
      <div className="uptime-chart">
        <h4>Uptime últimos 7 días</h4>
        <p style={{ textAlign: 'center', color: '#6b7280', padding: '2rem' }}>
          Sin datos suficientes (mínimo 2 días)
        </p>
      </div>
    );
  }

  return (
    <div className="uptime-chart">
      <h4>Uptime últimos 7 días</h4>
      <ResponsiveContainer width="100%" height={150}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="day" stroke="#6b7280" fontSize={12} />
          <YAxis 
            domain={[
              Math.max(0, Math.min(...chartData.map(d => d.uptime)) - 5),
              100
            ]}
            stroke="#6b7280" 
            fontSize={12}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#fff', 
              border: '1px solid #e5e7eb',
              borderRadius: '8px'
            }}
            formatter={(value) => `${value}%`}
            labelFormatter={(label) => {
              const item = chartData.find(d => d.day === label);
              return item ? `${item.day} (${item.checks} checks)` : label;
            }}
          />
          <Line 
            type="monotone" 
            dataKey="uptime" 
            stroke="#22c55e" 
            strokeWidth={2}
            dot={{ fill: '#22c55e', r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default UptimeChart;