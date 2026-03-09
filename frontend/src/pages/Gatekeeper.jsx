import React, { useState, useRef, useEffect } from 'react';
import { solveVDF, solveMemoryHard } from '../utils/cryptoSolvers';

const API_BASE = 'http://localhost:5000';

const StatusBadge = ({ status }) => {
  const configs = {
    idle: { color: 'bg-slate-500', text: 'Staged' },
    computing: { color: 'bg-blue-500 animate-pulse', text: 'Processing' },
    success: { color: 'bg-emerald-500', text: 'Verified' },
    error: { color: 'bg-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.4)]', text: 'Breached' },
  };
  const config = configs[status] || configs.idle;
  return (
    <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/50 border border-white/5">
      <div className={`w-2 h-2 rounded-full ${config.color}`} />
      <span className="text-[10px] uppercase tracking-widest font-bold text-slate-400">{config.text}</span>
    </div>
  );
};

export default function AegisQuantum() {
  const [activeScreen, setActiveScreen] = useState('start');
  const [status, setStatus] = useState('idle');
  const [logs, setLogs] = useState([]);
  const [progress, setProgress] = useState({ vdf: 0, memory: 0 });
  const [tamper, setTamper] = useState(false);
  const [vaultData, setVaultData] = useState(null);
  const [canProceed, setCanProceed] = useState(false);
  const [liveData, setLiveData] = useState({
    vdf: null, vdfResult: null,
    memory: null, memoryResult: null,
    quantum: null, quantumResult: null,
    metrics: {
      elapsed: 0,
      load: 0,
      entropy: 0,
      coherence: 0,
      stability: 0
    }
  });

  const logsEndRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    if (logsEndRef.current) logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  useEffect(() => {
    if (status === 'computing') {
      timerRef.current = setInterval(() => {
        setLiveData(prev => ({
          ...prev,
          metrics: {
            ...prev.metrics,
            elapsed: prev.metrics.elapsed + 0.1,
            load: Math.min(99, 45 + Math.random() * 50),
            entropy: 0.82 + Math.random() * 0.15,
            coherence: 0.95 + Math.random() * 0.04,
            stability: 0.99 - Math.random() * 0.02
          }
        }));
      }, 100);
    } else {
      clearInterval(timerRef.current);
    }
    return () => clearInterval(timerRef.current);
  }, [status]);

  const addLog = (msg, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString([], { hour12: false });
    setLogs((prev) => [...prev, { timestamp, msg, type }]);
  };

  const executeLayer1 = async () => {
    setActiveScreen('layer1');
    setStatus('computing');
    setCanProceed(false);
    setLogs([]);
    setProgress({ vdf: 0, memory: 0 });
    setLiveData({
      vdf: null, vdfResult: null, memory: null, memoryResult: null, quantum: null, quantumResult: null,
      metrics: { elapsed: 0, load: 0, entropy: 0, coherence: 0, stability: 0 }
    });

    try {
      addLog('INITIATING AEGIS QUANTUM HANDSHAKE', 'header');
      addLog('Synchronizing with remote resource firewall...', 'info');

      // VDF
      addLog('CRYPTO_ENGINE_ALPHA: Requesting VDF Challenge...', 'engine');
      let res = await fetch(`${API_BASE}/challenge/vdf`);
      if (!res.ok) throw new Error('VDF_CONNECTION_ERROR');
      let data = await res.json();
      setLiveData(prev => ({ ...prev, vdf: data.challenge }));

      const vdfSolution = await solveVDF(data.challenge, (p) => setProgress(prev => ({ ...prev, vdf: p })));
      setLiveData(prev => ({
        ...prev,
        vdfResult: {
          time: vdfSolution.solve_time,
          solution: String(vdfSolution.solution).substring(0, 16) + '...',
          checkpoints: vdfSolution.proof_chain.length
        }
      }));

      res = await fetch(`${API_BASE}/challenge/vdf/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          challenge_nonce: data.challenge.nonce,
          solution: vdfSolution.solution,
          proof_chain: vdfSolution.proof_chain
        })
      });
      if (!res.ok) throw new Error('VDF_INTEGRITY_FAILURE');
      addLog('Layer 1A Verified.', 'success');

      // Memory-Hard
      addLog('CRYPTO_ENGINE_BETA: Priming allocation buffer...', 'engine');
      res = await fetch(`${API_BASE}/challenge/memory-hard`);
      if (!res.ok) throw new Error('MEM_FIREWALL_UNREACHABLE');
      data = await res.json();
      setLiveData(prev => ({ ...prev, memory: data.challenge }));

      const memorySolution = await solveMemoryHard(data.challenge, (p) => setProgress(prev => ({ ...prev, memory: (p / 50000) * 100 })));
      setProgress(prev => ({ ...prev, memory: 100 }));
      setLiveData(prev => ({
        ...prev,
        memoryResult: {
          time: memorySolution.solve_time,
          solution: memorySolution.solution.substring(0, 20) + '...'
        }
      }));

      res = await fetch(`${API_BASE}/challenge/memory-hard/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          challenge_nonce: data.challenge.nonce,
          solution: memorySolution.solution
        })
      });
      if (!res.ok) throw new Error('MEM_HARD_VERIFY_ERROR');

      addLog('Layer 1B Verified. Firewall Decoupled.', 'success');
      addLog('PHASE 1 COMPLETE. PROCEED TO NEXT LAYER.', 'header');
      setStatus('success');
      setCanProceed(true);

    } catch (error) {
      addLog(`CRITICAL_FAILURE: ${error.message}`, 'error');
      setStatus('error');
    }
  };

  const executeLayer2 = async () => {
    setActiveScreen('layer2');
    setStatus('computing');
    setCanProceed(false);
    addLog('CRYPTO_ENGINE_OMEGA: Stabilizing Bell-State Entanglement...', 'engine');

    try {
      let res = await fetch(`${API_BASE}/challenge/quantum`);
      if (!res.ok) throw new Error('QUANTUM_AUTH_REJECTED');
      let data = await res.json();
      setLiveData(prev => ({ ...prev, quantum: data.challenge }));

      res = await fetch(`${API_BASE}/challenge/quantum/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ challenge: data.challenge, simulate_tamper: tamper })
      });

      const verifyData = await res.json();
      if (!res.ok) {
        setLiveData(prev => ({ ...prev, quantumResult: { fidelity: 0.000 } }));
        throw new Error(verifyData.detail || 'WAVEFUNCTION_COLLAPSE');
      }

      setLiveData(prev => ({ ...prev, quantumResult: verifyData }));
      addLog(`Fidelity Stabilized: ${verifyData.fidelity.toFixed(4)}`, 'success');
      addLog('VAULT_ENTRY_PERMITTED', 'header');
      setStatus('success');
      setCanProceed(true);

    } catch (error) {
      addLog(`COHERENCE_LOST: ${error.message}`, 'error');
      setStatus('error');
    }
  };

  const fetchVaultData = async () => {
    try {
      const res = await fetch(`${API_BASE}/protected`);
      if (!res.ok) throw new Error('ACCESS_FORBIDDEN');
      const data = await res.json();
      setVaultData(data.data);
      setActiveScreen('vault');
    } catch (error) {
      addLog('INTERNAL_VAULT_ERROR', 'error');
    }
  };

  return (
    <div className="min-h-screen bg-[#050508] flex items-center justify-center p-4">
      {/* Floating Background Glows */}
      <div className="fixed top-0 left-0 w-full h-full pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/10 blur-[120px] rounded-full animate-pulse-slow" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/10 blur-[120px] rounded-full animate-pulse-slow" style={{ animationDelay: '2s' }} />
      </div>

      {activeScreen === 'start' && (
        <div className="relative z-10 text-center animate-in fade-in zoom-in duration-700">
          <div className="mb-2 text-indigo-500 font-mono text-sm tracking-[0.4em] uppercase font-bold">Protocol Active</div>
          <h1 className="text-7xl font-bold text-white tracking-tighter mb-4">AEGIS<span className="text-indigo-500">QUANTUM</span></h1>
          <p className="text-slate-500 text-lg mb-12 max-w-md mx-auto font-light leading-relaxed">
            Advanced Intent-Based Authentication & Distributed Resource Firewall
          </p>
          <button onClick={executeLayer1} className="btn-primary scale-110">
            INITIALIZE AUTH_V1
          </button>
        </div>
      )}

      {activeScreen === 'layer1' && (
        <div className="relative z-10 w-full max-w-6xl grid grid-cols-12 gap-6 animate-in slide-in-from-bottom-8 duration-700">
          <div className="col-span-12 lg:col-span-8 flex flex-col gap-6">
            <div className="glass-panel p-8 flex flex-col gap-8 h-full">
              <div className="flex justify-between items-center border-b border-white/5 pb-6">
                <div>
                  <h2 className="text-2xl font-bold text-white uppercase tracking-tight">Phase 1: Dual-Core Firewall</h2>
                  <p className="text-slate-500 text-xs font-mono uppercase tracking-widest mt-1">Resource Validation Stage</p>
                </div>
                <StatusBadge status={status} />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className={`quantum-card p-6 ${liveData.vdf ? 'ring-1 ring-indigo-500/30' : ''}`}>
                  <h3 className="text-indigo-400 font-mono text-[10px] uppercase font-bold mb-4">Module Alpha // VDF</h3>
                  <div className="space-y-4">
                    <div className="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-indigo-500 transition-all duration-500" style={{ width: `${progress.vdf}%` }} />
                    </div>
                    {liveData.vdfResult ? (
                      <div className="text-[10px] text-emerald-400 font-mono font-bold animate-pulse">✓ Solution Verified: {liveData.vdfResult.time}s</div>
                    ) : <div className="text-[10px] text-slate-500 font-mono italic">Synchronizing cycles...</div>}
                  </div>
                </div>

                <div className={`quantum-card p-6 ${liveData.memory ? 'ring-1 ring-purple-500/30' : ''}`}>
                  <h3 className="text-purple-400 font-mono text-[10px] uppercase font-bold mb-4">Module Beta // Memory-Hard</h3>
                  <div className="space-y-4">
                    <div className="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-purple-500 transition-all duration-500" style={{ width: `${progress.memory}%` }} />
                    </div>
                    {liveData.memoryResult ? (
                      <div className="text-[10px] text-emerald-400 font-mono font-bold animate-pulse">✓ Entropy Matched: {liveData.memoryResult.time}s</div>
                    ) : <div className="text-[10px] text-slate-500 font-mono italic">Allocating buffers...</div>}
                  </div>
                </div>
              </div>

              {/* Enhanced Metrics Section for Layer 1 */}
              <div className="grid grid-cols-4 gap-4 py-6 border-y border-white/5">
                {[
                  { label: 'Total Elapsed', value: `${liveData.metrics.elapsed.toFixed(1)}s` },
                  { label: 'Compute Load', value: `${liveData.metrics.load.toFixed(1)}%` },
                  { label: 'Entropy Density', value: liveData.metrics.entropy.toFixed(3) },
                  { label: 'Gate Status', value: status === 'success' ? 'OPEN' : 'LOCKED' }
                ].map((m, i) => (
                  <div key={i} className="text-center">
                    <div className="text-[8px] text-slate-500 uppercase font-bold mb-1 tracking-widest">{m.label}</div>
                    <div className="text-xs font-mono text-indigo-300">{m.value}</div>
                  </div>
                ))}
              </div>

              <div className="mt-auto h-20 flex items-center justify-center">
                {canProceed ? (
                  <button onClick={executeLayer2} className="btn-primary animate-in fade-in slide-in-from-bottom-4 duration-500 bg-emerald-500 hover:bg-emerald-600 border-emerald-400/50 scale-110">
                    PROCEED TO PHASE 2 (SINGULARITY)
                  </button>
                ) : (
                  <p className="font-mono text-[10px] text-indigo-300 animate-pulse uppercase tracking-[0.2em]">
                    {status === 'computing' ? 'COMPUTING RESOURCE PROOFS...' : 'WAITING FOR INITIALIZATION...'}
                  </p>
                )}
              </div>
            </div>
          </div>

          <div className="col-span-12 lg:col-span-4 glass-panel p-6 flex flex-col h-full min-h-[400px]">
            <h3 className="text-indigo-400 font-mono text-[10px] uppercase font-bold mb-4 flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" /> Command Stream
            </h3>
            <div className="terminal-box flex-1">
              {logs.map((log, i) => (
                <div key={i} className="mb-2 text-[10px]">
                  <span className="text-slate-600 mr-2">[{log.timestamp}]</span>
                  <span className={log.type === 'header' ? 'text-indigo-400 font-bold' : log.type === 'engine' ? 'text-purple-400' : 'text-slate-400'}>{log.msg}</span>
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          </div>
        </div>
      )}

      {activeScreen === 'layer2' && (
        <div className="relative z-10 w-full max-w-4xl animate-in fade-in zoom-in duration-1000">
          <div className="glass-panel p-12 flex flex-col items-center gap-12 text-center bg-purple-500/[0.02] border-purple-500/20">
            <div>
              <div className="text-purple-500 font-mono text-xs tracking-[0.6em] uppercase font-bold mb-4 animate-pulse">Quantum Observation Required</div>
              <h2 className="text-5xl font-bold text-white tracking-tighter">PHASE 2: THE SINGULARITY</h2>
              <p className="text-slate-500 mt-4 max-w-md font-light">Measuring entanglement fidelity across the distributed quantum lattice.</p>
            </div>

            <div className="relative w-64 h-64 flex items-center justify-center">
              <div className="absolute inset-0 border-[1px] border-purple-500/10 rounded-full animate-pulse" />
              <div className="absolute inset-4 border-[1px] border-purple-500/20 rounded-full animate-pulse" style={{ animationDelay: '0.5s' }} />
              <div className="absolute inset-0 border-t-2 border-purple-500 rounded-full animate-spin duration-[3000ms]" />
              <div className="text-5xl text-purple-400 drop-shadow-[0_0_15px_rgba(168,85,247,0.5)]">⚛</div>
            </div>

            <div className="w-full max-w-2xl space-y-8">
              <div className="grid grid-cols-3 gap-8 py-6 border-y border-white/5">
                {[
                  { label: 'Coherence Time', value: `${liveData.metrics.coherence.toFixed(4)}ms` },
                  { label: 'Phase Stability', value: `${(liveData.metrics.stability * 100).toFixed(2)}%` },
                  { label: 'Lattice Sync', value: 'STABLE_01' }
                ].map((m, i) => (
                  <div key={i} className="text-left">
                    <div className="text-[8px] text-slate-500 uppercase font-bold mb-1 tracking-widest">{m.label}</div>
                    <div className="text-xs font-mono text-purple-300">{m.value}</div>
                  </div>
                ))}
              </div>

              <div className="space-y-4">
                <div className="flex justify-between font-mono text-[10px] text-slate-500">
                  <span className="uppercase font-bold tracking-widest">Entanglement Fidelity</span>
                  <span className={liveData.quantumResult?.fidelity >= 0.85 ? 'text-emerald-400 font-bold' : 'text-purple-400 animate-pulse'}>
                    {liveData.quantumResult ? liveData.quantumResult.fidelity.toFixed(4) : 'MEASURING...'}
                  </span>
                </div>
                <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden">
                  <div className="h-full bg-purple-500 transition-all duration-1000" style={{ width: liveData.quantumResult ? `${liveData.quantumResult.fidelity * 100}%` : '40%' }} />
                </div>
              </div>

              <div className="pt-8 h-20 flex items-center justify-center">
                {canProceed ? (
                  <button onClick={fetchVaultData} className="btn-primary animate-in fade-in slide-in-from-bottom-4 duration-500 bg-rose-600 hover:bg-rose-700 border-rose-400/50 scale-110">
                    ACCESS NUCLEAR ARCHIVES
                  </button>
                ) : (
                  <div className="flex justify-center gap-8 animate-pulse">
                    <div className="text-left">
                      <div className="text-[8px] text-slate-600 uppercase font-bold tracking-widest">Observer State</div>
                      <div className="text-[10px] text-purple-300 font-mono">OBSERVING_WAVEFUNCTION...</div>
                    </div>
                    <div className="text-left border-l border-white/5 pl-8">
                      <div className="text-[8px] text-slate-600 uppercase font-bold tracking-widest">Entanglement Node</div>
                      <div className="text-[10px] text-purple-300 font-mono">QT-NODE-01</div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="w-full pt-8 border-t border-white/5">
              <p className="font-mono text-[9px] text-purple-400/60 uppercase tracking-[0.3em]">
                Secure Channel: {liveData.quantumResult ? 'CRYPTO_LINK_STABLE' : 'CALIBRATING_QUBITS_0x992...'}
              </p>
            </div>
          </div>
        </div>
      )}

      {activeScreen === 'vault' && vaultData && (
        <div className="relative z-10 w-full max-w-7xl grid grid-cols-12 gap-6 animate-in zoom-in-95 duration-1000">
          <div className="col-span-12 glass-panel overflow-hidden border-rose-500/20 bg-rose-500/[0.02]">
            <div className="bg-rose-950/40 p-8 flex justify-between items-center border-b border-rose-500/30">
              <div className="text-left">
                <div className="text-rose-500 font-mono text-[10px] tracking-[0.4em] uppercase font-bold mb-1 animate-pulse">Classified Access Granted</div>
                <h2 className="text-4xl font-bold text-white tracking-tighter">{vaultData.project}</h2>
              </div>
              <div className="text-right font-mono text-[10px]">
                <div className="text-rose-300/60 uppercase">Clearance: {vaultData.classification}</div>
                <div className="text-rose-500 mt-1 font-bold">NODE: LNL-CORE-10 // 0xAF92...11C</div>
              </div>
            </div>
          </div>

          <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
            <div className="glass-panel p-6 border-rose-500/10">
              <h3 className="text-rose-400 font-mono text-[10px] uppercase font-bold tracking-widest mb-6 border-b border-white/5 pb-2">Reactor Core Telemetry</h3>
              <div className="space-y-6">
                {[
                  { label: 'Thermal Stability', value: '98.4%', progress: 98, color: 'bg-emerald-500' },
                  { label: 'Neutron Flux', value: '1.24e15 n/cm²s', progress: 75, color: 'bg-rose-500' },
                  { label: 'Coolant Pressure', value: '8.4 MPa', progress: 82, color: 'bg-rose-500' },
                  { label: 'Enrichment Level', value: 'U-235 (19.75%)', progress: 20, color: 'bg-indigo-500' },
                ].map((item, idx) => (
                  <div key={idx}>
                    <div className="flex justify-between text-[10px] text-slate-400 mb-2 font-mono">
                      <span>{item.label}</span>
                      <span className="text-rose-300 font-bold">{item.value}</span>
                    </div>
                    <div className="h-1 w-full bg-slate-900 rounded-full overflow-hidden">
                      <div className={`h-full ${item.color} transition-all duration-1000`} style={{ width: `${item.progress}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-panel p-6 bg-rose-500/[0.01]">
              <h3 className="text-rose-400 font-mono text-[10px] uppercase font-bold tracking-widest mb-4">Facility Lockdown</h3>
              <div className="grid grid-cols-2 gap-4">
                {['Perimeter Alpha', 'Sec-Vault 7', 'Enrichment Wing', 'Waste Storage'].map((floor, i) => (
                  <div key={i} className="bg-black/40 border border-white/5 p-3 rounded-lg flex items-center gap-3">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                    <span className="text-[10px] text-slate-400 font-mono">{floor}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="col-span-12 lg:col-span-8">
            <div className="glass-panel p-12 h-full flex flex-col items-center justify-center text-center bg-rose-500/[0.01]">
              <div className="mb-8 w-24 h-24 border-2 border-rose-500/10 rounded-full flex items-center justify-center relative">
                <div className="absolute inset-0 border-2 border-rose-500 border-t-transparent rounded-full animate-spin" />
                <span className="text-rose-500 text-4xl font-bold">☢</span>
              </div>

              <div className="max-w-xl">
                <p className="text-rose-300/40 font-mono text-[10px] mb-4 uppercase tracking-[0.4em]">Confidential Payload Hash</p>
                <h3 className="text-white text-5xl font-bold tracking-tight mb-8 leading-tight">
                  {vaultData.confidential_payload}
                </h3>

                <div className="grid grid-cols-3 gap-6 pt-8 border-t border-white/5">
                  <div className="text-center">
                    <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Last Access</div>
                    <div className="text-rose-200 font-mono text-xs">0.4s ago</div>
                  </div>
                  <div className="text-center">
                    <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Fidelity</div>
                    <div className="text-rose-200 font-mono text-xs">0.9998</div>
                  </div>
                  <div className="text-center">
                    <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Enc Type</div>
                    <div className="text-rose-200 font-mono text-xs">AEGIS-IV</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="col-span-12 h-20 flex items-center justify-center">
            <button onClick={() => {
              setActiveScreen('start');
              setStatus('idle');
              setCanProceed(false);
              setVaultData(null);
            }} className="btn-primary opacity-50 hover:opacity-100 transition-opacity">
              RE-INITIALIZE PROTOCOL
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
