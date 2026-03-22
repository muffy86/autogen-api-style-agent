<script lang="ts">
</script>

<div class="wallpaper">
  <div class="nebula"></div>
  <div class="stars"></div>
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

  .stars {
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
</style>
