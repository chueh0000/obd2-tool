import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LineChart, Line, ResponsiveContainer, YAxis, Tooltip, Legend } from 'recharts';
import { Activity, Car, Clock, Wifi, WifiOff, Zap, Gauge, Droplet, Wind, Waves, Cpu, LayoutGrid } from 'lucide-react';
import AnalogGaugeCluster from './AnalogGaugeCluster';

interface PIDData {
  value: number | string;
  unit: string;
  pid: string;
  cluster?: string;
  dynamic?: boolean;
  group?: string;
  min?: number;
  max?: number;
}

interface PIDHistory {
  name: string;
  unit: string;
  pid: string;
  cluster: string;
  dynamic: boolean;
  group: string;
  min?: number;
  max?: number;
  currentValue: number | string;
  history: { time: string; value: number }[];
}

const COLORS = ['#818cf8', '#60a5fa', '#22d3ee', '#a78bfa', '#fbbf24', '#fb923c'];

const getClusterIcon = (clusterName: string) => {
  switch (clusterName) {
    case 'Engine Performance': return <Gauge size={18} />;
    case 'Fuel System': return <Droplet size={18} />;
    case 'O2 Sensors': return <Waves size={18} />;
    case 'Emissions': return <Wind size={18} />;
    case 'Vehicle Info': return <Car size={18} />;
    case 'System': return <Cpu size={18} />;
    default: return <Activity size={18} />;
  }
};

const getValueColor = (val: number | string, min?: number, max?: number) => {
  if (typeof val !== 'number') return 'text-white';
  if (min !== undefined && max !== undefined) {
    if (val < min || val > max) return 'text-rose-400';
    return 'text-emerald-400';
  }
  // Fallback: negative is red, otherwise default
  if (val < 0) return 'text-rose-400';
  return 'text-white';
};

const TickerText = ({ text, className = '' }: { text: string; className?: string }) => {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const textRef = React.useRef<HTMLSpanElement>(null);
  const [isOverflowing, setIsOverflowing] = useState(false);

  useEffect(() => {
    const checkOverflow = () => {
      if (containerRef.current && textRef.current) {
        const textWidth = textRef.current.scrollWidth;
        const containerWidth = containerRef.current.clientWidth;
        setIsOverflowing(textWidth > containerWidth + 2);
      }
    };
    checkOverflow();
    // Re-check after layout shifts
    const timer = setTimeout(checkOverflow, 100);
    window.addEventListener('resize', checkOverflow);
    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', checkOverflow);
    };
  }, [text]);

  return (
    <div ref={containerRef} className={`overflow-hidden whitespace-nowrap w-full group/ticker relative ${className}`} title={text}>
      <div className={`inline-flex ${isOverflowing ? 'animate-ticker group-hover/ticker:[animation-play-state:paused]' : ''}`}>
        <span ref={textRef} className={isOverflowing ? 'pr-12' : ''}>{text}</span>
        {isOverflowing && <span className="pr-12">{text}</span>}
      </div>
    </div>
  );
};

export default function Dashboard() {
  const [connected, setConnected] = useState(false);
  const [viewMode, setViewMode] = useState<'digital' | 'analog'>('digital');
  const [dataMap, setDataMap] = useState<Record<string, PIDHistory>>({});
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<string>('All');

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = host.includes('5173') ? 'ws://localhost:8000/ws' : `${protocol}//${host}/ws`;
    
    let ws = new WebSocket(wsUrl);

    ws.onopen = () => setConnected(true);

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const timestamp = payload.timestamp ? new Date(payload.timestamp * 1000) : new Date();
        const timeStr = timestamp.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit', fractionalSecondDigits: 1 });
        setLastUpdate(timestamp);

        setDataMap((prev) => {
          const next = { ...prev };
          Object.keys(payload).forEach((key) => {
            if (key === 'timestamp') return;
            const item = payload[key] as PIDData;
            if (!item || item.value === undefined) return;
            
            let numVal = typeof item.value === 'number' ? item.value : parseFloat(item.value as string);
            if (isNaN(numVal)) numVal = 0;

            if (!next[key]) {
              next[key] = {
                name: key,
                unit: item.unit,
                pid: item.pid,
                cluster: item.cluster || 'Uncategorized',
                dynamic: item.dynamic !== undefined ? item.dynamic : true,
                group: item.group || key,
                min: item.min,
                max: item.max,
                currentValue: item.value,
                history: []
              };
            } else {
              next[key] = { ...next[key] };
            }
            
            next[key].currentValue = item.value;
            next[key].history = [...next[key].history, { time: timeStr, value: numVal }];
            
            if (next[key].history.length > 50) {
              next[key].history = next[key].history.slice(-50);
            }
          });
          return next;
        });
      } catch (err) {
        console.error("Error parsing websocket data", err);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      setTimeout(() => setConnected(false), 2000);
    };

    return () => ws.close();
  }, []);

  const pids = Object.values(dataMap);
  const clusters = ['All', ...Array.from(new Set(pids.map(p => p.cluster)))].sort((a, b) => {
    if (a === 'All') return -1;
    if (b === 'All') return 1;
    return a.localeCompare(b);
  });

  // Sorting for "All" view
  let filteredPids = selectedCluster === 'All' ? pids : pids.filter(p => p.cluster === selectedCluster);
  if (selectedCluster === 'All') {
    filteredPids.sort((a, b) => a.pid.localeCompare(b.pid));
  }

  // Grouping logic for specific clusters
  const isGroupedView = selectedCluster !== 'All';
  const groupedPids: Record<string, PIDHistory[]> = {};
  
  if (isGroupedView) {
    filteredPids.forEach(p => {
      if (!groupedPids[p.group]) groupedPids[p.group] = [];
      groupedPids[p.group].push(p);
    });
  }

  const renderGroupedCard = (groupName: string, groupItems: PIDHistory[]) => {
    const isDynamic = groupItems.some(item => item.dynamic);

    // Sub-group dynamic items by unit so metrics with different units get their own chart
    const itemsByUnit: Record<string, PIDHistory[]> = {};
    groupItems.forEach(item => {
      const u = item.unit || 'unitless';
      if (!itemsByUnit[u]) itemsByUnit[u] = [];
      itemsByUnit[u].push(item);
    });

    const hasMultipleUnits = Object.keys(itemsByUnit).length > 1;

    return (
      <Card key={groupName} className={`bg-slate-900/80 border-slate-800 backdrop-blur-xl overflow-hidden group hover:border-slate-700 transition-colors ${!isDynamic ? 'h-fit' : ''}`}>
        <CardHeader className="pb-2">
          <div className="flex justify-between items-start w-full min-w-0">
            <div className="w-full min-w-0 overflow-hidden">
              <p className="text-xs font-mono text-indigo-400 mb-1">
                {groupItems.map(i => i.pid).join(', ')} • {groupItems[0].cluster}
              </p>
              <CardTitle className="text-lg font-medium text-slate-200 w-full min-w-0" title={groupName}>
                <TickerText text={groupName} />
              </CardTitle>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className={`grid gap-4 ${groupItems.length > 1 ? 'grid-cols-2' : 'grid-cols-1'} ${isDynamic ? 'mb-4' : 'mb-2'}`}>
            {groupItems.map((pid, idx) => (
              <div key={pid.pid} className="flex flex-col min-w-0">
                {groupItems.length > 1 && (
                  <TickerText text={pid.name} className="text-xs text-slate-500 mb-1" />
                )}
                <div className="flex items-baseline gap-2">
                  <span className={`font-bold tracking-tight tabular-nums ${getValueColor(pid.currentValue, pid.min, pid.max)} ${!isDynamic && typeof pid.currentValue === 'string' && pid.currentValue.length > 10 ? 'text-xl' : (groupItems.length > 1 ? 'text-2xl' : 'text-4xl')}`}>
                    {typeof pid.currentValue === 'number' && !Number.isInteger(pid.currentValue) 
                      ? pid.currentValue.toFixed(2) 
                      : pid.currentValue}
                  </span>
                  <span className="text-xs text-slate-500 font-medium">{pid.unit}</span>
                </div>
              </div>
            ))}
          </div>
          
          {Object.entries(itemsByUnit).map(([unit, unitItems], unitIdx) => {
            const dynamicUnitItems = unitItems.filter(item => item.dynamic);
            if (dynamicUnitItems.length === 0) return null;

            const combinedHistory: any[] = [];
            if (dynamicUnitItems[0].history.length > 0) {
              for (let i = 0; i < dynamicUnitItems[0].history.length; i++) {
                const point: any = { time: dynamicUnitItems[0].history[i].time };
                dynamicUnitItems.forEach(item => {
                  if (item.history[i]) {
                    point[item.name] = item.history[i].value;
                  }
                });
                combinedHistory.push(point);
              }
            }

            return (
              <div key={unit} className={`${hasMultipleUnits ? 'mt-4 pt-2 border-t border-slate-800/60' : ''}`}>
                {hasMultipleUnits && (
                  <TickerText 
                    text={`${dynamicUnitItems.map(i => i.name).join(' & ')} (${unit})`} 
                    className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold mb-1 font-mono" 
                  />
                )}
                <div className="h-28 w-full opacity-80 group-hover:opacity-100 transition-opacity">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={combinedHistory}>
                      {dynamicUnitItems.map((pid, idx) => (
                        <Line 
                          key={pid.name}
                          type="monotone" 
                          dataKey={pid.name} 
                          stroke={COLORS[(unitIdx * 2 + idx) % COLORS.length]} 
                          strokeWidth={2} 
                          dot={false}
                          isAnimationActive={false} 
                        />
                      ))}
                      <YAxis domain={['auto', 'auto']} hide />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#f8fafc' }}
                        itemStyle={{ color: '#e2e8f0' }}
                        labelStyle={{ display: 'none' }}
                      />
                      {dynamicUnitItems.length > 1 && (
                        <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '6px' }} />
                      )}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>
    );
  };

  const renderSingleCard = (pid: PIDHistory) => {
    return renderGroupedCard(pid.name, [pid]);
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-50 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className={`bg-slate-900 border-r border-slate-800 flex-col hidden md:flex transition-all duration-500 ease-in-out z-20 overflow-hidden ${viewMode === 'digital' ? 'w-64 opacity-100' : 'w-0 opacity-0 border-transparent'}`}>
        <div className="w-64 p-4 flex flex-col h-full shrink-0">
          <div className="flex items-center gap-2 mb-8 text-indigo-400">
          <Activity size={24} />
          <h1 className="text-xl font-bold tracking-wider">OBD2 LIVE</h1>
        </div>
        
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">Categories</h2>
        <div className="flex-1 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
          {pids.length === 0 ? (
            <p className="text-slate-600 text-sm">Waiting for data...</p>
          ) : (
            clusters.map((cluster) => {
              const count = cluster === 'All' ? pids.length : pids.filter(p => p.cluster === cluster).length;
              return (
                <button
                  key={cluster}
                  onClick={() => setSelectedCluster(cluster)}
                  className={`w-full text-left p-3 rounded-lg flex items-center gap-3 transition-colors border ${selectedCluster === cluster ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-400' : 'bg-slate-800/50 hover:bg-slate-800 border-slate-700/50 text-slate-300'}`}
                >
                  <div className={selectedCluster === cluster ? 'text-indigo-400' : 'text-slate-500'}>
                    {getClusterIcon(cluster)}
                  </div>
                  <span className="text-sm font-medium flex-1 truncate">{cluster}</span>
                  <Badge variant="secondary" className="bg-slate-950/50 text-xs border border-slate-700/50">{count}</Badge>
                </button>
              );
            })
          )}
        </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Header */}
        <header className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md flex items-center justify-between px-6 shrink-0">
          <div className="flex items-center gap-4">
            <Badge variant={connected ? "default" : "destructive"} className={connected ? "bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20 border-emerald-500/20" : ""}>
              {connected ? <Wifi size={14} className="mr-1" /> : <WifiOff size={14} className="mr-1" />}
              {connected ? 'Connected' : 'Disconnected'}
            </Badge>
            <div className="text-sm text-slate-400 flex items-center gap-1">
              <Car size={14} />
              <span>ISO 15031</span>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setViewMode(v => v === 'digital' ? 'analog' : 'digital')}
              className="flex bg-slate-950 rounded-lg p-1 border border-slate-800 cursor-pointer hover:border-slate-700 transition-colors group focus:outline-none"
              title="Toggle View"
            >
              <div className={`flex items-center justify-center p-1.5 rounded-md transition-colors ${viewMode === 'digital' ? 'bg-indigo-500/20 text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'}`}>
                <LayoutGrid size={16} />
              </div>
              <div className={`flex items-center justify-center p-1.5 rounded-md transition-colors ${viewMode === 'analog' ? 'bg-indigo-500/20 text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'}`}>
                <Gauge size={16} />
              </div>
            </button>
            <div className="text-sm text-slate-400 flex items-center gap-1 font-mono">
              <Clock size={14} />
              {lastUpdate ? lastUpdate.toLocaleTimeString() : '--:--:--'}
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="relative flex-1 overflow-hidden">
          {/* Digital View */}
          {viewMode === 'digital' && (
            <div className="absolute inset-0 flex flex-col animate-fade-in bg-slate-950">
              <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-br from-slate-950 to-slate-900 custom-scrollbar">
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 items-start">
                  {selectedCluster === 'All' 
                    ? filteredPids.map(renderSingleCard)
                    : Object.keys(groupedPids).map(groupName => renderGroupedCard(groupName, groupedPids[groupName]))
                  }
                  
                  {pids.length === 0 && (
                    <div className="col-span-full h-64 flex flex-col items-center justify-center border-2 border-dashed border-slate-800 rounded-xl text-slate-500 bg-slate-900/30">
                      <Activity size={48} className="mb-4 opacity-50 animate-pulse" />
                      <p>Waiting for OBD2 data stream...</p>
                      <p className="text-sm mt-2 opacity-70 font-mono">python src/diagnostics/live_data.py monitor</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Analog View */}
          {viewMode === 'analog' && (
            <div className="absolute inset-0 flex flex-col animate-fade-in bg-slate-950">
              <AnalogGaugeCluster dataMap={dataMap} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
