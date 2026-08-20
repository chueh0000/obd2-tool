import React, { useMemo, useState, useEffect } from 'react';

const UserIcon = ({ name, size = 32, scale = 1 }: { name: string, size?: number, scale?: number }) => (
  <img 
    src={`/icons/${name}.png`} 
    style={{ 
      width: size, 
      height: size, 
      objectFit: 'contain',
      transform: `scale(${scale})`
    }} 
    alt={name} 
    className="select-none pointer-events-none drop-shadow-[0_0_5px_rgba(255,255,255,0.4)]"
  />
);

interface GaugeProps {
  value: number;
  min: number;
  max: number;
  title: string;
  unit: string;
  size?: number;
  majorTicks?: number;
  minorTicks?: number;
  dangerZone?: [number, number];
  className?: string;
  tickFontSize?: number;
  valueFormatter?: (v: number) => string | number;
  labelFormatter?: (v: number) => string | number;
}

const AnalogGauge: React.FC<GaugeProps> = ({
  value,
  min,
  max,
  title,
  icon,
  unit,
  size = 200,
  majorTicks = 10,
  minorTicks = 4,
  dangerZone,
  className = '',
  tickFontSize = 11,
  labelFormatter = (v) => Math.round(v)
}) => {
  const [sweepPhase, setSweepPhase] = useState<'init' | 'peak' | 'return' | 'normal'>('init');

  useEffect(() => {
    const t1 = setTimeout(() => setSweepPhase('peak'), 250); 
    const t2 = setTimeout(() => setSweepPhase('return'), 1000); 
    const t3 = setTimeout(() => setSweepPhase('normal'), 1800); 
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, []);

  const displayValue = 
    sweepPhase === 'init' || sweepPhase === 'return' ? min : 
    sweepPhase === 'peak' ? max : 
    value;

  const startAngle = -135;
  const angleRange = 270;
  
  const clamp = (val: number) => Math.min(Math.max(val, min), max);
  const getAngle = (val: number) => startAngle + ((clamp(val) - min) / (max - min)) * angleRange;

  const rotation = getAngle(displayValue);

  const transitionStyle = sweepPhase === 'normal' 
    ? 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)' 
    : 'transform 0.75s cubic-bezier(0.4, 0, 0.2, 1)';

  const ticks = useMemo(() => {
    const t = [];
    const step = (max - min) / majorTicks;
    const minorStep = step / (minorTicks + 1);

    for (let i = 0; i <= majorTicks; i++) {
      const val = min + i * step;
      const angle = getAngle(val);
      const isDanger = dangerZone ? val >= dangerZone[0] && val <= dangerZone[1] : false;
      t.push({ type: 'major', val, angle, isDanger });

      if (i < majorTicks) {
        for (let j = 1; j <= minorTicks; j++) {
          const minorVal = val + j * minorStep;
          const minorAngle = getAngle(minorVal);
          const isMinorDanger = dangerZone ? minorVal >= dangerZone[0] && minorVal <= dangerZone[1] : false;
          t.push({ type: 'minor', val: minorVal, angle: minorAngle, isDanger: isMinorDanger });
        }
      }
    }
    return t;
  }, [min, max, majorTicks, minorTicks, dangerZone]);

  return (
    <div 
      className={`relative flex flex-col items-center justify-center bg-slate-900 rounded-full shadow-[0_10px_40px_-10px_rgba(0,0,0,0.8)] border-[6px] border-slate-800 shrink-0 ${className}`} 
      style={{ width: size, height: size }}
    >
      {/* Outer Inner Glow / Bezel effect */}
      <div className="absolute inset-0 rounded-full shadow-[inset_0_0_30px_rgba(0,0,0,0.9)] border border-slate-700/50 pointer-events-none z-10"></div>
      
      {/* Carbon fiber / Texture background approximation */}
      <div className="absolute inset-0 rounded-full opacity-5 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)', backgroundSize: '4px 4px' }}></div>

      <svg viewBox="0 0 200 200" className="absolute inset-0 w-full h-full drop-shadow-lg z-0">
        {/* Ticks */}
        {ticks.map((tick, i) => {
          const isMajor = tick.type === 'major';
          const length = isMajor ? 14 : 7;
          const strokeWidth = isMajor ? 2.5 : 1.5;
          const color = tick.isDanger ? '#ef4444' : '#f1f5f9'; // red-500 or slate-100
          
          return (
            <g key={i} transform={`rotate(${tick.angle} 100 100)`}>
              <line 
                x1="100" y1="12" 
                x2="100" y2={12 + length} 
                stroke={color} 
                strokeWidth={strokeWidth}
                strokeLinecap="round"
                className={tick.isDanger ? 'drop-shadow-[0_0_6px_rgba(239,68,68,0.9)]' : 'drop-shadow-[0_0_3px_rgba(255,255,255,0.6)]'}
              />
              {isMajor && (
                <text 
                  x="100" y="44" 
                  textAnchor="middle" 
                  fill={color} 
                  fontSize={tickFontSize} 
                  fontWeight="bold" 
                  transform={`rotate(${-tick.angle} 100 44)`}
                  className="font-mono tracking-tighter"
                  style={{ textShadow: tick.isDanger ? '0 0 8px rgba(239,68,68,0.8)' : '0 0 5px rgba(255,255,255,0.4)' }}
                >
                  {labelFormatter(tick.val)}
                </text>
              )}
            </g>
          );
        })}

        {/* Needle */}
        <g 
          style={{ transform: `rotate(${rotation}deg)`, transformOrigin: '100px 100px', transition: transitionStyle }}
          className="will-change-transform"
        >
          {/* Needle shadow */}
          <polygon points="97,115 103,115 101,18 99,18" fill="rgba(0,0,0,0.5)" transform="translate(3, 5)" />
          {/* Needle body */}
          <polygon points="96,115 104,115 100.5,16 99.5,16" fill="#ef4444" className="drop-shadow-[0_0_5px_rgba(239,68,68,1)]" />
          {/* Center cap */}
          <circle cx="100" cy="100" r="14" fill="#0f172a" stroke="#334155" strokeWidth="2" className="drop-shadow-lg" />
          <circle cx="100" cy="100" r="6" fill="#1e293b" />
        </g>
      </svg>

      {/* Icon/Title and Unit */}
      <div className="absolute bottom-[10%] flex flex-col items-center justify-center text-slate-400 z-20 pointer-events-none w-full">
        {icon ? (
          <div className="mt-1 opacity-80 drop-shadow-sm">{icon}</div>
        ) : title ? (
          <div className="text-[9px] sm:text-[10px] font-bold tracking-[0.2em] uppercase text-center drop-shadow-sm mt-1">{title}</div>
        ) : null}
        {unit && (
          <div className="text-[9px] sm:text-[10px] font-bold uppercase tracking-widest opacity-60 drop-shadow-sm">
            {unit}
          </div>
        )}
      </div>
    </div>
  );
};

// --- Cluster Component ---

export interface PIDHistory {
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

interface AnalogGaugeClusterProps {
  dataMap: Record<string, PIDHistory>;
}

export default function AnalogGaugeCluster({ dataMap }: AnalogGaugeClusterProps) {
  const getValue = (key: string) => {
    const item = dataMap[key];
    if (item && typeof item.currentValue === 'number') return item.currentValue;
    if (item && typeof item.currentValue === 'string') return parseFloat(item.currentValue) || 0;
    return 0;
  };

  const rpm = getValue('Engine RPM');
  const speed = getValue('Vehicle speed');
  const fuel = getValue('Fuel Tank Level Input');
  const voltage = getValue('Control module voltage');
  const coolantTemp = getValue('Engine coolant temperature');
  const oilTemp = getValue('Engine oil temperature');

  return (
    <div className="flex-1 w-full h-full flex flex-col items-center justify-center bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black p-4 sm:p-8 overflow-y-auto custom-scrollbar">
      <div className="w-full max-w-6xl mx-auto flex flex-col items-center justify-center gap-8 sm:gap-12 min-h-min py-8">
        
        {/* Main Gauges (RPM and Speed) */}
        <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16 w-full">
          <AnalogGauge 
            value={rpm} 
            min={0} 
            max={8000} 
            title="x1000 r/min" 
            size={300} 
            majorTicks={8} 
            minorTicks={4} 
            dangerZone={[6500, 8000]} 
            labelFormatter={(v) => v >= 1000 ? (v / 1000).toFixed(0) : v.toString()}
            className="md:w-[400px] md:h-[400px] lg:w-[480px] lg:h-[480px]"
          />
          <AnalogGauge 
            value={speed} 
            min={0} 
            max={240} 
            title="KM/H" 
            size={300} 
            majorTicks={12} 
            minorTicks={1} 
            dangerZone={[200, 240]}
            labelFormatter={(v) => v.toFixed(0)}
            className="md:w-[400px] md:h-[400px] lg:w-[480px] lg:h-[480px]"
          />
        </div>

        {/* Auxiliary Gauges */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-10 w-full max-w-4xl px-4">
          <AnalogGauge 
            value={fuel} 
            min={0} 
            max={100} 
            icon={<UserIcon name="fuel" size={22} scale={1.3} />}
            size={150} 
            majorTicks={4} 
            minorTicks={1} 
            tickFontSize={15}
            dangerZone={[0, 15]} 
            labelFormatter={(v) => {
               if (v === 0) return 'E';
               if (v === 50) return '1/2';
               if (v === 100) return 'F';
               return '';
            }}
            className="mx-auto sm:w-[180px] sm:h-[180px]"
          />
          <AnalogGauge 
            value={voltage} 
            min={8} 
            max={16} 
            icon={<UserIcon name="battery" size={22} scale={0.9} />}
            size={150} 
            majorTicks={4} 
            minorTicks={1} 
            tickFontSize={15}
            dangerZone={[8, 11]} // Low voltage is danger
            labelFormatter={(v) => v.toFixed(0)}
            className="mx-auto sm:w-[180px] sm:h-[180px]"
          />
          <AnalogGauge 
            value={coolantTemp} 
            min={40} 
            max={140} 
            icon={<UserIcon name="coolant" size={22} scale={0.9} />}
            size={150} 
            majorTicks={5} 
            minorTicks={1} 
            tickFontSize={15}
            dangerZone={[110, 140]}
            labelFormatter={(v) => v.toFixed(0)}
            className="mx-auto sm:w-[180px] sm:h-[180px]"
          />
          <AnalogGauge 
            value={oilTemp} 
            min={40} 
            max={140} 
            icon={<UserIcon name="oil" size={22} scale={0.9} />}
            size={150} 
            majorTicks={5} 
            minorTicks={1} 
            tickFontSize={15}
            dangerZone={[120, 140]}
            labelFormatter={(v) => v.toFixed(0)}
            className="mx-auto sm:w-[180px] sm:h-[180px]"
          />
        </div>
      </div>
    </div>
  );
}
