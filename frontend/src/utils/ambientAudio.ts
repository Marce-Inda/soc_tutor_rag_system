/**
 * Dynamic Ambient Audio Engine - SOC Tutor
 * Handles background music loops and cross-fades.
 */

class AmbientMusicManager {
  private ambient: HTMLAudioElement | null = null;
  private action: HTMLAudioElement | null = null;
  private currentMode: 'ambient' | 'action' = 'ambient';
  private isStarted: boolean = false;
  private fadeInterval: any = null;

  constructor() {
    if (typeof window !== 'undefined') {
      this.ambient = new Audio('/audio/Submerged_Systems.mp3');
      this.action = new Audio('/audio/Digital_Breach_Protocol.mp3');
      
      [this.ambient, this.action].forEach(audio => {
        audio.loop = true;
        audio.volume = 0;
      });
    }
  }

  /**
   * Arranca el motor de música (Requiere interacción previa del usuario)
   */
  start() {
    if (this.isStarted || !this.ambient) return;
    
    this.isStarted = true;
    this.ambient.play().catch(e => console.warn("Autoplay blocked, waiting for interaction."));
    this.action?.play().catch(() => {}); // Play silently in background
    
    this.fadeTo('ambient');
  }

  /**
   * Transición suave entre temas
   */
  private fadeTo(target: 'ambient' | 'action', durationMs: number = 3000) {
    if (this.fadeInterval) clearInterval(this.fadeInterval);
    
    const steps = 20;
    const intervalTime = durationMs / steps;
    const targetAmbientVol = target === 'ambient' ? 0.15 : 0;
    const targetActionVol = target === 'action' ? 0.25 : 0;

    this.fadeInterval = setInterval(() => {
      if (!this.ambient || !this.action) return;

      const ambStep = (targetAmbientVol - this.ambient.volume) / 5;
      const actStep = (targetActionVol - this.action.volume) / 5;

      this.ambient.volume = Math.max(0, Math.min(1, this.ambient.volume + ambStep));
      this.action.volume = Math.max(0, Math.min(1, this.action.volume + actStep));

      // Close enough check
      if (Math.abs(this.ambient.volume - targetAmbientVol) < 0.01 && 
          Math.abs(this.action.volume - targetActionVol) < 0.01) {
        this.ambient.volume = targetAmbientVol;
        this.action.volume = targetActionVol;
        clearInterval(this.fadeInterval);
      }
    }, intervalTime);
  }

  escalate() {
    if (this.currentMode === 'action') return;
    this.currentMode = 'action';
    this.fadeTo('action');
  }

  deescalate() {
    if (this.currentMode === 'ambient') return;
    this.currentMode = 'ambient';
    this.fadeTo('ambient');
  }

  stopAll() {
    if (this.fadeInterval) clearInterval(this.fadeInterval);
    [this.ambient, this.action].forEach(a => {
      if (a) {
        a.pause();
        a.currentTime = 0;
      }
    });
    this.isStarted = false;
  }
}

export const musicManager = new AmbientMusicManager();
