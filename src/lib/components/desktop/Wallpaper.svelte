<script lang="ts">
  let starShadows = $state('');
  let twinkleStars = $state<{ x: number; y: number; delay: number; size: number }[]>([]);

  function generateStars() {
    const shadows: string[] = [];
    for (let i = 0; i < 100; i++) {
      const x = Math.round(Math.random() * 2000);
      const y = Math.round(Math.random() * 1200);
      const opacity = 0.15 + Math.random() * 0.35;
      shadows.push(`${x}px ${y}px 0 0 rgba(255,255,255,${opacity.toFixed(2)})`);
    }
    starShadows = shadows.join(',');

    const tStars: typeof twinkleStars = [];
    for (let i = 0; i < 5; i++) {
      tStars.push({
        x: 10 + Math.random() * 80,
        y: 5 + Math.random() * 85,
        delay: Math.random() * 5,
        size: 1.5 + Math.random() * 1.5
      });
    }
    twinkleStars = tStars;
  }

  $effect(() => {
    generateStars();
  });
</script>

<div class="wallpaper">
  <div class="nebula"></div>
  <div class="conic-nebula"></div>
  <div class="stars-field" style="box-shadow: {starShadows};"></div>
  <div class="stars-bg"></div>
  {#each twinkleStars as star}
    <div
      class="twinkle-star"
      style="
        left: {star.x}%;
        top: {star.y}%;
        width: {star.size}px;
        height: {star.size}px;
        animation-delay: {star.delay}s;
      "
    ></div>
  {/each}
  <div class="aurora"></div>
</div>

<style>
  .wallpaper {
    position: fixed;
    inset: 0;
    background: var(--bg-base);
    z-index: 0;
    overflow: hidden;
  }

  .nebula {
    position: absolute;
    inset: -20%;
    background:
      radial-gradient(ellipse at 20% 50%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 20%, rgba(99, 102, 241, 0.07) 0%, transparent 50%),
      radial-gradient(ellipse at 50% 80%, rgba(168, 85, 247, 0.06) 0%, transparent 50%),
      radial-gradient(ellipse at 70% 60%, rgba(79, 70, 229, 0.05) 0%, transparent 40%),
      radial-gradient(ellipse at 30% 30%, rgba(139, 92, 246, 0.04) 0%, transparent 45%);
    animation: nebula 30s ease-in-out infinite alternate;
  }

  .conic-nebula {
    position: absolute;
    top: 20%;
    left: 30%;
    width: 60%;
    height: 60%;
    background: conic-gradient(
      from 0deg,
      rgba(139, 92, 246, 0.04),
      rgba(99, 102, 241, 0.02),
      rgba(168, 85, 247, 0.04),
      rgba(79, 70, 229, 0.02),
      rgba(139, 92, 246, 0.04)
    );
    border-radius: 50%;
    filter: blur(60px);
    animation: conicSpin 60s linear infinite;
    opacity: 0.6;
  }

  .stars-field {
    position: absolute;
    width: 1px;
    height: 1px;
    top: 0;
    left: 0;
    background: transparent;
  }

  .stars-bg {
    position: absolute;
    inset: 0;
    background-image:
      radial-gradient(1px 1px at 10% 15%, rgba(255, 255, 255, 0.15), transparent),
      radial-gradient(1px 1px at 25% 35%, rgba(255, 255, 255, 0.1), transparent),
      radial-gradient(1px 1px at 45% 10%, rgba(255, 255, 255, 0.12), transparent),
      radial-gradient(1px 1px at 60% 45%, rgba(255, 255, 255, 0.08), transparent),
      radial-gradient(1px 1px at 75% 25%, rgba(255, 255, 255, 0.1), transparent),
      radial-gradient(1px 1px at 85% 65%, rgba(255, 255, 255, 0.06), transparent),
      radial-gradient(1px 1px at 15% 70%, rgba(255, 255, 255, 0.08), transparent),
      radial-gradient(1px 1px at 35% 85%, rgba(255, 255, 255, 0.07), transparent),
      radial-gradient(1px 1px at 55% 55%, rgba(255, 255, 255, 0.09), transparent),
      radial-gradient(1px 1px at 90% 80%, rgba(255, 255, 255, 0.06), transparent),
      radial-gradient(1.5px 1.5px at 40% 60%, rgba(167, 139, 250, 0.15), transparent),
      radial-gradient(1.5px 1.5px at 70% 40%, rgba(139, 92, 246, 0.12), transparent);
  }

  .twinkle-star {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.8);
    box-shadow: 0 0 4px rgba(255, 255, 255, 0.4);
    animation: twinkle 3s ease-in-out infinite;
  }

  .aurora {
    position: absolute;
    bottom: 20%;
    left: -10%;
    width: 120%;
    height: 120px;
    background: linear-gradient(
      90deg,
      transparent 0%,
      rgba(139, 92, 246, 0.06) 20%,
      rgba(99, 102, 241, 0.08) 40%,
      rgba(168, 85, 247, 0.05) 60%,
      rgba(79, 70, 229, 0.06) 80%,
      transparent 100%
    );
    filter: blur(40px);
    animation: aurora 20s ease-in-out infinite;
    opacity: 0.5;
  }
</style>
