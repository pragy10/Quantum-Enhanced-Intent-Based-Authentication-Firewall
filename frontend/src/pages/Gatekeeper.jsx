import React, { useState, useRef, useEffect } from 'react';
import { solveVDF, solveMemoryHard } from '../utils/cryptoSolvers';

const API_BASE = 'http://localhost:8000';

export default function Gatekeeper() {
  const [activeScreen, setActiveScreen] = useState('start');
  const [status, setStatus] = useState('idle'); 
  const [logs, setLogs] = useState([]);
  const [progress, setProgress] = useState({ vdf: 0, memory: 0 });
  const [tamper, setTamper] = useState(false);
  const [vaultData, setVaultData] = useState(null);
  
  // Added total time state
  const [totalTime, setTotalTime] = useState(null);
  
  // Expanded liveData to hold the results for the UI boxes!
  const [liveData, setLiveData] = useState({
    vdf: null,
    vdfResult: null,
    memory: null,
    memoryResult: null,
    quantum: null,
    quantumResult: null
  });
  
  const logsEndRef = useRef(null);

  useEffect(() => {
    if (logsEndRef.current) logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const addLog = (msg) => {
    setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
  };

  // ==========================================
  // LAYER 1: VDF & MEMORY HARD FIREWALL
  // ==========================================
  const executeLayer1 = async () => {
    setActiveScreen('layer1');
    setStatus('computing');
    setLogs([]);
    setProgress({ vdf: 0, memory: 0 });
    setTotalTime(null);
    setLiveData({ vdf: null, vdfResult: null, memory: null, memoryResult: null, quantum: null, quantumResult: null });
    
    try {
      const startTime = Date.now();
      addLog('='.repeat(60));
      addLog('HYBRID CRYPTOGRAPHIC AUTHENTICATION INITIATED');
      addLog('='.repeat(60));

      // ------------------------------------------
      // 1. VDF Challenge
      // ------------------------------------------
      addLog('[LAYER 1A] Verifiable Delay Function Challenge');
      let res = await fetch(`${API_BASE}/challenge/vdf`);
      if (!res.ok) throw new Error('Failed to fetch VDF challenge');
      let data = await res.json();
      
      setLiveData(prev => ({ ...prev, vdf: data.challenge })); 
      addLog(`Challenge Received | Nonce: ${data.challenge.nonce.substring(0, 10)}...`);
      addLog('Computing VDF Proof Chain (Non-parallelizable)...');
      
      const vdfSolution = await solveVDF(data.challenge, (p) => setProgress(prev => ({ ...prev, vdf: p })));
      
      // Save the VDF result strictly for the UI box
      setLiveData(prev => ({ 
        ...prev, 
        vdfResult: {
          time: vdfSolution.solve_time,
          solution: String(vdfSolution.solution).substring(0, 20) + '...',
          checkpoints: vdfSolution.proof_chain.length
        }
      }));
      
      addLog(`VDF COMPUTATION COMPLETE in ${vdfSolution.solve_time}s`);
      
      res = await fetch(`${API_BASE}/challenge/vdf/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          challenge_nonce: data.challenge.nonce,
          solution: vdfSolution.solution,
          proof_chain: vdfSolution.proof_chain
        })
      });
      if (!res.ok) throw new Error('VDF Verification Failed');
      addLog('[SUCCESS] VDF Verification Passed.');
      addLog('-'.repeat(60));

      // ------------------------------------------
      // 2. Memory-Hard Challenge
      // ------------------------------------------
      addLog('[LAYER 1B] Memory-Hard Challenge');
      res = await fetch(`${API_BASE}/challenge/memory-hard`);
      if (!res.ok) throw new Error('Failed to fetch Memory-Hard challenge');
      data = await res.json();
      
      setLiveData(prev => ({ ...prev, memory: data.challenge })); 
      addLog(`Challenge Received | Target Prefix: "${data.challenge.target_prefix}"`);
      addLog('Allocating Memory and Computing Hashes...');
      
      const memorySolution = await solveMemoryHard(data.challenge, (p) => setProgress(prev => ({ ...prev, memory: (p / 50000) * 100 })));
      
      setProgress(prev => ({ ...prev, memory: 100 }));
      
      // Save the Memory result strictly for the UI box
      setLiveData(prev => ({
        ...prev,
        memoryResult: {
          time: memorySolution.solve_time,
          solution: memorySolution.solution.substring(0, 24) + '...'
        }
      }));
      
      addLog(`MEMORY-HARD COMPUTATION COMPLETE in ${memorySolution.solve_time}s`);
      
      res = await fetch(`${API_BASE}/challenge/memory-hard/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          challenge_nonce: data.challenge.nonce,
          solution: memorySolution.solution
        })
      });
      if (!res.ok) throw new Error('Memory-Hard Verification Failed');
      addLog('[SUCCESS] Memory-Hard Verification Passed.');

      const tTime = ((Date.now() - startTime) / 1000).toFixed(2);
      setTotalTime(tTime); // Set total time for the UI
      
      addLog('='.repeat(60));
      addLog(`LAYER 1 CLEARED. Total Time: ${tTime}s`);
      addLog('Awaiting manual authorization to proceed to Quantum Layer.');
      addLog('='.repeat(60));

      setStatus('success');

    } catch (error) {
      addLog(`[FAILED] ERROR: ${error.message}`);
      setStatus('error');
    }
  };

  const proceedToLayer2 = () => {
    setActiveScreen('layer2');
    setStatus('idle');
    setLogs([]);
  };

  // ==========================================
  // LAYER 2: QUANTUM AUTHENTICATION
  // ==========================================
  const executeLayer2 = async () => {
    setStatus('computing');
    addLog('Initiating Quantum Bell-State Entanglement...');
    
    try {
      let res = await fetch(`${API_BASE}/challenge/quantum`);
      if (!res.ok) throw new Error('Unauthorized for Quantum Layer');
      let data = await res.json();
      
      setLiveData(prev => ({ ...prev, quantum: data.challenge })); 
      addLog(`Encoding phase into Qubit 1...`);
      
      res = await fetch(`${API_BASE}/challenge/quantum/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          challenge: data.challenge,
          simulate_tamper: tamper
        })
      });
      
      const verifyData = await res.json();
      
      // --- THE FIX IS HERE ---
      if (!res.ok) {
        // If the server blocks us, force the fidelity to 0.000 so the UI turns red instead of crashing!
        setLiveData(prev => ({ ...prev, quantumResult: { fidelity: 0.000 } })); 
        throw new Error(verifyData.detail || 'Quantum Collapse Detected');
      }
      
      // If successful, set the real fidelity data
      setLiveData(prev => ({ ...prev, quantumResult: verifyData })); 
      
      addLog(`✅ Quantum Correlation Verified!`);
      addLog('='.repeat(60));
      addLog(`LAYER 2 CLEARED. Vault access granted.`);
      addLog('='.repeat(60));
      
      setStatus('success');

    } catch (error) {
      addLog(`❌ SECURITY BREACH: ${error.message}`);
      setStatus('error');
    }
  };

  const fetchVaultData = async () => {
    try {
      const res = await fetch(`${API_BASE}/protected`);
      if (!res.ok) throw new Error('Access Denied to Vault');
      const data = await res.json();
      setVaultData(data.data);
      setActiveScreen('vault');
    } catch (error) {
      setStatus('error');
    }
  };

  const renderTerminal = () => (
    <div className="bg-black/90 border border-primary/30 rounded-lg p-3 h-40 overflow-y-auto font-mono text-xs text-green-400 shadow-inner mt-4">
      {logs.map((log, i) => <div key={i}>{log}</div>)}
      <div ref={logsEndRef} />
    </div>
  );

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6 font-sans">
      
      {/* SCREEN 1: START */}
      {activeScreen === 'start' && (
        <div className="max-w-xl w-full text-center space-y-8 animate-fade-in">
          <h1 className="text-5xl font-bold text-white tracking-tight">Gatekeeper<span className="text-primary">OS</span></h1>
          <p className="text-gray-400 text-lg">High-Security Research Laboratory Gateway</p>
          <button onClick={executeLayer1} className="w-full bg-primary hover:bg-primaryHover text-white py-4 rounded-lg font-bold text-lg tracking-wide shadow-[0_0_20px_rgba(99,102,241,0.4)] transition-all">
            INITIATE SECURE HANDSHAKE
          </button>
        </div>
      )}

      {/* SCREEN 2: LAYER 1 FIREWALL */}
      {activeScreen === 'layer1' && (
        <div className="max-w-3xl w-full bg-card border border-primary/20 rounded-2xl p-8 shadow-2xl animate-fade-in">
          <h2 className="text-2xl font-bold text-white mb-6 border-b border-gray-700 pb-2">Layer 1: Resource Firewall</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {/* VDF UI DISPLAY */}
            <div className={`p-4 rounded-lg border flex flex-col justify-between ${liveData.vdf ? 'border-primary/50 bg-primary/10' : 'border-gray-800 bg-gray-900'} transition-colors`}>
              <div>
                <h3 className="text-primary font-mono font-bold mb-2">VDF Engine</h3>
                {liveData.vdf ? (
                  <div className="font-mono text-xs text-gray-300 space-y-1">
                    <div><span className="text-gray-500">Nonce:</span> {liveData.vdf.nonce.substring(0, 12)}...</div>
                    <div><span className="text-gray-500">Modulus:</span> {String(liveData.vdf.modulus).length} Digits</div>
                    <div><span className="text-gray-500">Iterations:</span> {liveData.vdf.time_parameter.toLocaleString()}</div>
                  </div>
                ) : <div className="text-xs text-gray-600 font-mono">Awaiting parameters...</div>}
                
                <div className="mt-4">
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>Computation</span><span>{progress.vdf}%</span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-1.5">
                    <div className="bg-primary h-1.5 rounded-full transition-all duration-300" style={{ width: `${progress.vdf}%` }}></div>
                  </div>
                </div>
              </div>

              {/* VDF RESULT UI (Appears when done) */}
              {liveData.vdfResult && (
                <div className="mt-4 pt-3 border-t border-primary/30 font-mono text-xs space-y-1 animate-fade-in">
                  <div className="text-green-400 font-bold">✓ Solved in {liveData.vdfResult.time}s</div>
                  <div className="text-gray-400"><span className="text-gray-500">Result:</span> {liveData.vdfResult.solution}</div>
                  <div className="text-gray-400"><span className="text-gray-500">Checkpoints:</span> {liveData.vdfResult.checkpoints} verified</div>
                </div>
              )}
            </div>

            {/* MEMORY HARD UI DISPLAY */}
            <div className={`p-4 rounded-lg border flex flex-col justify-between ${liveData.memory ? 'border-purple-500/50 bg-purple-500/10' : 'border-gray-800 bg-gray-900'} transition-colors`}>
              <div>
                <h3 className="text-purple-400 font-mono font-bold mb-2">Memory-Hard Engine</h3>
                {liveData.memory ? (
                  <div className="font-mono text-xs text-gray-300 space-y-1">
                    <div><span className="text-gray-500">Hash Cost:</span> {liveData.memory.memory_cost / 1024} MB</div>
                    <div><span className="text-gray-500">Prefix Target:</span> "{liveData.memory.target_prefix}"</div>
                    <div><span className="text-gray-500">Algorithm:</span> SHA-256 Chained</div>
                  </div>
                ) : <div className="text-xs text-gray-600 font-mono">Awaiting parameters...</div>}

                <div className="mt-4">
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>Allocation</span><span>{Math.min(100, progress.memory).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-1.5">
                    <div className="bg-purple-500 h-1.5 rounded-full transition-all duration-300" style={{ width: `${Math.min(100, progress.memory)}%` }}></div>
                  </div>
                </div>
              </div>

              {/* MEMORY RESULT UI (Appears when done) */}
              {liveData.memoryResult && (
                <div className="mt-4 pt-3 border-t border-purple-500/30 font-mono text-xs space-y-1 animate-fade-in">
                  <div className="text-green-400 font-bold">✓ Solved in {liveData.memoryResult.time}s</div>
                  <div className="text-gray-400"><span className="text-gray-500">Hash Match:</span> {liveData.memoryResult.solution}</div>
                </div>
              )}
            </div>
          </div>
          
          {renderTerminal()}

          {/* MANUAL PROCEED BUTTON & TOTAL TIME FOR LAYER 1 */}
          {status === 'success' && (
            <div className="mt-6 text-center animate-fade-in">
              <div className="inline-block bg-green-900/20 border border-green-500/40 text-green-400 px-6 py-2 rounded-lg mb-4 font-mono text-sm shadow-[0_0_15px_rgba(34,197,94,0.2)]">
                TOTAL LAYER 1 TIME: <span className="font-bold text-white">{totalTime} SECONDS</span>
              </div>
              <button 
                onClick={proceedToLayer2} 
                className="w-full bg-green-600 hover:bg-green-500 text-white py-4 rounded-lg font-bold text-lg tracking-wide transition-all shadow-[0_0_20px_rgba(34,197,94,0.4)] hover:shadow-[0_0_30px_rgba(34,197,94,0.6)]">
                AUTHORIZE NEXT LAYER
              </button>
            </div>
          )}
        </div>
      )}

      {/* SCREEN 3: LAYER 2 QUANTUM */}
      {activeScreen === 'layer2' && (
        <div className="max-w-3xl w-full bg-card border border-purple-500/30 rounded-2xl p-8 shadow-[0_0_40px_rgba(168,85,247,0.15)] animate-fade-in">
          <h2 className="text-2xl font-bold text-white mb-6 border-b border-gray-700 pb-2 flex items-center gap-3">
            <span className="text-purple-500 text-3xl">⚛</span> Layer 2: Quantum Handshake
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {/* QUANTUM STATE UI */}
            <div className="p-4 rounded-lg border border-purple-500/40 bg-purple-900/10">
              <h3 className="text-purple-400 font-mono font-bold mb-3 border-b border-purple-500/20 pb-1">Bell-State Parameters</h3>
              {liveData.quantum ? (
                <div className="font-mono text-xs text-gray-300 space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Challenge String:</span>
                    <span>{liveData.quantum.substring(0, 12)}...</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Derived Phase Angle:</span>
                    <span className="text-blue-300">{(parseInt(liveData.quantum.substring(0,8), 16) % 360)}° (RZ Gate)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Required Fidelity:</span>
                    <span>≥ 0.850</span>
                  </div>
                </div>
              ) : (
                <div className="text-xs text-gray-600 font-mono">Awaiting Quantum Channel...</div>
              )}
            </div>

            {/* LIVE MEASUREMENT UI */}
            <div className="p-4 rounded-lg border border-gray-700 bg-black/50 relative overflow-hidden">
              <h3 className="text-gray-400 font-mono font-bold mb-3">Measurement ⟨Z⊗Z⟩</h3>
              {liveData.quantumResult ? (
                <div className="flex flex-col items-center justify-center h-full pb-4">
                  <div className={`text-4xl font-mono font-bold ${liveData.quantumResult.fidelity >= 0.85 ? 'text-green-400' : 'text-red-500'}`}>
                    {(liveData.quantumResult.fidelity).toFixed(3)}
                  </div>
                  <div className="text-xs text-gray-500 mt-1 uppercase tracking-widest">
                    {liveData.quantumResult.fidelity >= 0.85 ? 'Entanglement Verified' : 'State Collapsed / Tampered'}
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full pb-4 text-xs text-gray-600 font-mono animate-pulse">
                  Observing Qubits...
                </div>
              )}
            </div>
          </div>

          <div className="bg-red-950/30 p-4 rounded-lg border border-red-900/50 mb-6 flex items-center justify-between">
            <div>
              <div className="text-red-400 font-bold text-sm">MITM Attack Simulation</div>
              <div className="text-gray-400 text-xs">Injects RX(π/4) interference on wire 1 to break entanglement.</div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" checked={tamper} onChange={(e) => setTamper(e.target.checked)} disabled={status === 'computing'} className="sr-only peer" />
              <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
            </label>
          </div>

          {/* TOGGLE BUTTONS BASED ON STATUS */}
          {status !== 'success' && (
            <button 
              onClick={executeLayer2} 
              disabled={status === 'computing'}
              className="w-full bg-gradient-to-r from-purple-700 to-indigo-600 hover:from-purple-600 hover:to-indigo-500 disabled:opacity-50 text-white py-4 rounded-lg font-bold text-lg tracking-wide transition-all shadow-lg"
            >
              {status === 'computing' ? 'MEASURING...' : 'ESTABLISH ENTANGLEMENT'}
            </button>
          )}

          {status === 'success' && (
            <div className="mt-6 text-center animate-fade-in">
              <button 
                onClick={fetchVaultData} 
                className="w-full bg-green-600 hover:bg-green-500 text-white py-4 rounded-lg font-bold text-lg tracking-wide transition-all shadow-[0_0_20px_rgba(34,197,94,0.4)] hover:shadow-[0_0_30px_rgba(34,197,94,0.6)]">
                ACCESS CLASSIFIED VAULT
              </button>
            </div>
          )}

          {renderTerminal()}
        </div>
      )}

      {/* SCREEN 4: THE VAULT */}
      {activeScreen === 'vault' && vaultData && (
        <div className="max-w-4xl w-full animate-fade-in">
          <div className="bg-red-900/20 border border-red-500/50 rounded-t-2xl p-4 text-center">
            <span className="text-red-500 tracking-[0.3em] font-bold uppercase">{vaultData.classification} CLEARANCE GRANTED</span>
          </div>
          <div className="bg-card border-x border-b border-gray-800 rounded-b-2xl p-8 shadow-2xl">
            <h2 className="text-3xl font-bold text-white mb-2">{vaultData.project}</h2>
            <p className="text-gray-400 font-mono text-sm mb-8">Access Token Valid. Session logged at {new Date(vaultData.timestamp * 1000).toLocaleString()}</p>
            
            <div className="bg-gray-900 border border-gray-700 p-6 rounded-xl">
              <h3 className="text-primary font-semibold mb-4 text-lg">Confidential Payload</h3>
              <p className="text-white text-xl font-mono">{vaultData.confidential_payload}</p>
            </div>
          </div>
        </div>
      )}
      
    </div>
  );
}