/**
 * Yields control to the browser to prevent UI freezing during heavy loops
 */
const yieldToBrowser = () => new Promise(resolve => setTimeout(resolve, 0));

/**
 * SHA-256 hash function using native Web Crypto API
 */
async function sha256(message) {
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer); 
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Solves the Memory-Hard Challenge (Argon2 simulation)
 */
export const solveMemoryHard = async (challenge, onProgress) => {
    const { salt, target_prefix, memory_cost } = challenge;
    const startTime = Date.now();
    let attempt = 0;
    
    while (attempt < 50000) {
        const candidate = `${salt}:${attempt}`;
        let hash = await sha256(candidate);
        
        
        for (let i = 0; i < 1000; i++) {
            hash = await sha256(hash); 
        }
        
        const finalHash = await sha256(hash);
        
        if (finalHash.startsWith(target_prefix)) {
            const solveTime = ((Date.now() - startTime) / 1000).toFixed(2);
            return {
                solution: candidate,
                solve_time: parseFloat(solveTime)
            };
        }
        
        
        if (attempt % 500 === 0) {
            if (onProgress) onProgress(attempt);
            await yieldToBrowser(); 
        }
        attempt++;
    }
    
    throw new Error('Memory-Hard solve timeout'); 
};

/**
 * Solves the Verifiable Delay Function (VDF) Challenge
 */
export const solveVDF = async (challenge, onProgress) => {
    const { modulus, base, time_parameter } = challenge;
    
    
    const N = BigInt(modulus); 
    const g = BigInt(base); 
    const T = time_parameter;
    
    let result = g % N;
    const proofChain = [result.toString()];
    const proofInterval = 1000; 
    const startTime = Date.now();
    
    
    for (let i = 0; i < T; i++) {
        result = (result * result) % N; 
        
        
        if ((i + 1) % proofInterval === 0) {
            proofChain.push(result.toString()); 
        }
        
        
        if ((i + 1) % 25000 === 0) { 
            const progress = ((i + 1) / T * 100).toFixed(1);
            if (onProgress) onProgress(progress);
        }
        
        if ((i + 1) % 500 === 0) {
            await yieldToBrowser(); 
        }
    }
    
    if (proofChain[proofChain.length - 1] !== result.toString()) {
        proofChain.push(result.toString()); 
    }
    
    const solveTime = ((Date.now() - startTime) / 1000).toFixed(2);
    
    return {
        solution: result.toString(),
        proof_chain: proofChain,
        solve_time: parseFloat(solveTime)
    };
};