<template>
  <div 
    data-theme="borg" 
    class="relative h-screen w-screen font-sans bg-cover bg-center"
    :style="`background-image: url('${borgBg}')`"
  >
    <div class="absolute top-4 right-4 z-10">
      <div class="dropdown dropdown-end">
        <label tabindex="0" class="btn btn-ghost btn-square m-1 border-2 border-neon-green text-neon-green hover:bg-neon-green hover:text-borg-black">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4h16v2H4zM4 11h16v2H4zM4 18h16v2H4z" />
          </svg>
        </label>
        <div tabindex="0" class="dropdown-content menu p-4 shadow-lg bg-base-100 rounded-none border-2 border-neon-green w-72">
          <div class="form-control">
            <label class="label">
              <span class="label-text text-neon-green">Grid Width (Lx)</span>
            </label>
            <input type="number" v-model.number="lx" min="4" max="50" class="input input-bordered w-full bg-transparent border-neon-green text-neon-green" />
          </div>
          <div class="form-control mt-4">
            <label class="label">
              <span class="label-text text-neon-green">Grid Height (Ly)</span>
            </label>
            <input type="number" v-model.number="ly" min="4" max="50" class="input input-bordered w-full bg-transparent border-neon-green text-neon-green" />
          </div>
          <div class="form-control mt-4">
            <label class="label">
              <span class="label-text text-neon-green">N</span>
            </label>
            <input type="number" v-model.number="n" :max="lx" min="0" class="input input-bordered w-full bg-transparent border-neon-green text-neon-green" />
          </div>
          <button @click="generateConfiguration" class="btn btn-primary mt-6 border-2 border-neon-green" :disabled="isLoading">
            <span v-if="isLoading" class="loading loading-spinner"></span>
            <span v-else>ASSIMILATE GRID</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-borg-black bg-opacity-90 z-20">
      <span class="loading loading-spinner text-neon-green loading-lg"></span>
    </div>

    <canvas ref="canvas" class="absolute top-0 left-0 w-full h-full" :class="{ 'opacity-10': isLoading }"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import borgBg from '@/assets/borglatticebackground.png';

const lx = ref(8);
const ly = ref(8);
const n = ref(4);
const canvas = ref(null);
let model = null;
const isLoading = ref(false);
let animationFrameId = null;

function updateN() {
  n.value = Math.floor(lx.value / 2);
}

watch(lx, updateN);

async function generateConfiguration() {
  if (!lx.value || !ly.value || isLoading.value) return;
  
  isLoading.value = true;
  
  try {
    const response = await fetch('http://localhost:8000/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ Lx: lx.value, Ly: ly.value, n: n.value }),
    });
    const data = await response.json();
    
    model = {
      Lx: lx.value,
      Ly: ly.value,
      n: n.value,
      verticalSpins: data.verticalSpins,
      horizontalSpins: data.horizontalSpins,
    };

  } catch (error) {
    console.error("Failed to generate configuration:", error);
  } finally {
    isLoading.value = false;
  }
}

const colorPalette = ['#39ff14', '#ffdd00', '#ff0000', '#00d8ff', '#39ff14'];
function palette(value) {
  const scaledValue = value * (colorPalette.length - 1);
  const index1 = Math.floor(scaledValue);
  const index2 = Math.min(Math.ceil(scaledValue), colorPalette.length - 1);
  const t = scaledValue - index1;

  const color1 = colorPalette[index1];
  const color2 = colorPalette[index2];

  const r1 = parseInt(color1.slice(1, 3), 16);
  const g1 = parseInt(color1.slice(3, 5), 16);
  const b1 = parseInt(color1.slice(5, 7), 16);

  const r2 = parseInt(color2.slice(1, 3), 16);
  const g2 = parseInt(color2.slice(3, 5), 16);
  const b2 = parseInt(color2.slice(5, 7), 16);

  const r = Math.round(r1 + (r2 - r1) * t);
  const g = Math.round(g1 + (g2 - g1) * t);
  const b = Math.round(b1 + (b2 - b1) * t);

  return `rgb(${r}, ${g}, ${b})`;
}

function getGridColor(x, y, time) {
    const wave1 = (Math.sin(x * 0.005 + y * 0.002 + time * 0.0002) + 1) / 2;
    const wave2 = (Math.sin(x * 0.003 - y * 0.004 + time * 0.0003) + 1) / 2;
    const combined = (wave1 + wave2) / 2;
    return palette(combined);
}


function draw(time) {
  if (!canvas.value || !model) return;
  const ctx = canvas.value.getContext('2d');
  const parent = canvas.value.parentElement;
  
  if (canvas.value.width !== parent.clientWidth || canvas.value.height !== parent.clientHeight) {
    canvas.value.width = parent.clientWidth;
    canvas.value.height = parent.clientHeight;
  }
  
  const width = canvas.value.width;
  const height = canvas.value.height;

  ctx.clearRect(0, 0, width, height);

  const gridSpacing = Math.min(width / (model.Lx + 1), height / (model.Ly + 1));
  const offsetX = (width - (model.Lx - 1) * gridSpacing) / 2;
  const offsetY = (height - (model.Ly - 1) * gridSpacing) / 2;

  function drawDiamondNode(ctx, x, y, size) {
    ctx.beginPath();
    ctx.moveTo(x, y - size); ctx.lineTo(x + size, y); ctx.lineTo(x, y + size); ctx.lineTo(x - size, y);
    ctx.closePath();
    ctx.stroke();
  }

  function drawAnomalyGlyph(ctx, x, y, size) {
    const angleStep = (Math.PI * 2) / 3;
    ctx.beginPath();
    for (let i = 0; i < 3; i++) {
      const angle = angleStep * i - Math.PI / 2;
      const pointX = x + Math.cos(angle) * size;
      const pointY = y + Math.sin(angle) * size;
      i === 0 ? ctx.moveTo(pointX, pointY) : ctx.lineTo(pointX, pointY);
    }
    ctx.closePath();
    ctx.fill();
  }

  const arrowWidth = gridSpacing * 0.05;
  function drawBorgArrow(ctx, x1, y1, x2, y2, color) {
    ctx.strokeStyle = color;
    ctx.lineWidth = arrowWidth;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
    const angle = Math.atan2(y2 - y1, x2 - x1);
    const headLength = gridSpacing * 0.25;
    ctx.beginPath();
    ctx.moveTo(x2, y2);
    ctx.lineTo(x2 - headLength * Math.cos(angle - Math.PI / 12), y2 - headLength * Math.sin(angle - Math.PI / 12));
    ctx.moveTo(x2, y2);
    ctx.lineTo(x2 - headLength * Math.cos(angle + Math.PI / 12), y2 - headLength * Math.sin(angle + Math.PI / 12));
    ctx.stroke();
  }

  // Draw conduits (Arrows) FIRST
  for (let i = 0; i < model.Ly; i++) {
    for (let j = 0; j < model.Lx; j++) {
      const vX = offsetX + j * gridSpacing;
      const vY = offsetY + i * gridSpacing - gridSpacing / 2;
      const vSpin = model.verticalSpins[i][j];
      const vArrowLength = gridSpacing * 0.5;
      const vColor = getGridColor(vX, vY, time);
      drawBorgArrow(ctx, vX, vY - vArrowLength / 2 * vSpin, vX, vY + vArrowLength / 2 * vSpin, vColor);
      
      const hX = offsetX + j * gridSpacing - gridSpacing / 2;
      const hY = offsetY + i * gridSpacing;
      const hSpin = model.horizontalSpins[i][j];
      const hArrowLength = gridSpacing * 0.5;
      const hColor = getGridColor(hX, hY, time);
      drawBorgArrow(ctx, hX - hArrowLength / 2 * hSpin, hY, hX + hArrowLength / 2 * hSpin, hY, hColor);
    }
  }

  // Draw vertex nodes SECOND
  ctx.strokeStyle = '#4d0000';
  ctx.lineWidth = gridSpacing * 0.03;
  for (let i = 0; i < model.Ly; i++) {
    for (let j = 0; j < model.Lx; j++) {
      drawDiamondNode(ctx, offsetX + j * gridSpacing, offsetY + i * gridSpacing, gridSpacing * 0.1);
    }
  }

  const defects = [];
  for (let i = 0; i < model.Ly; i++) {
    for (let j = 0; j < model.Lx; j++) {
      const sublattice = (j + i) % 2;
      const vSpin = model.verticalSpins[i][j];
      if ((sublattice === 0 && vSpin === -1) || (sublattice === 1 && vSpin === 1)) {
        defects.push({ id: defects.length, x: offsetX + j * gridSpacing, y: offsetY + i * gridSpacing - gridSpacing / 2 });
      }
      const hSpin = model.horizontalSpins[i][j];
      if ((sublattice === 0 && hSpin === -1) || (sublattice === 1 && hSpin === 1)) {
        defects.push({ id: defects.length, x: offsetX + j * gridSpacing - gridSpacing / 2, y: offsetY + i * gridSpacing });
      }
    }
  }

  const adj = new Map(defects.map(d => [d.id, []]));
  const tolerance = gridSpacing * 0.1;
  const expectedDist = gridSpacing / Math.sqrt(2);
  for (let i = 0; i < defects.length; i++) {
    for (let j = i + 1; j < defects.length; j++) {
      const d1 = defects[i];
      const d2 = defects[j];
      const dist = Math.sqrt(Math.pow(d2.x - d1.x, 2) + Math.pow(d2.y - d1.y, 2));
      if (Math.abs(dist - expectedDist) < tolerance) {
        adj.get(d1.id).push(d2.id);
        adj.get(d2.id).push(d1.id);
      }
    }
  }

  const clusters = [];
  const visited = new Set();
  for (const defect of defects) {
    if (!visited.has(defect.id)) {
      const currentCluster = [];
      const stack = [defect.id];
      visited.add(defect.id);
      while (stack.length > 0) {
        const u = stack.pop();
        currentCluster.push(u);
        for (const v of adj.get(u)) {
          if (!visited.has(v)) {
            visited.add(v);
            stack.push(v);
          }
        }
      }
      clusters.push(currentCluster);
    }
  }

  ctx.fillStyle = '#00d8ff';
  ctx.shadowColor = '#00d8ff';
  ctx.shadowBlur = 15;
  defects.forEach(d => {
    drawAnomalyGlyph(ctx, d.x, d.y, gridSpacing * 0.15);
  });
  
  const baseThickness = gridSpacing * 0.02;
  const increment = gridSpacing * 0.025;
  ctx.strokeStyle = '#00d8ff';
  
  clusters.forEach(cluster => {
    if (cluster.length < 2) return;
    ctx.lineWidth = baseThickness + (cluster.length - 2) * increment;
    
    const drawnEdges = new Set();
    cluster.forEach(u_id => {
      adj.get(u_id).forEach(v_id => {
        const edge = [u_id, v_id].sort().join('-');
        if (!drawnEdges.has(edge)) {
          const u_defect = defects[u_id];
          const v_defect = defects[v_id];
          ctx.beginPath();
          ctx.moveTo(u_defect.x, u_defect.y);
          ctx.lineTo(v_defect.x, v_defect.y);
          ctx.stroke();
          drawnEdges.add(edge);
        }
      });
    });
  });

  ctx.shadowBlur = 0;
}

function animate(time) {
  draw(time);
  animationFrameId = requestAnimationFrame(animate);
}

onMounted(async () => {
  await generateConfiguration();
  animationFrameId = requestAnimationFrame(animate);
});

onUnmounted(() => {
  if (animationFrameId) cancelAnimationFrame(animationFrameId);
});
</script>