/* web/game.js
   Minimal JS port/prototype of the Pygame project core loop.
   - deterministic seeded level generator
   - tile rendering
   - player controls and physics (simplified)
   - NPC spawn and simple AI
   - basic powerups and saving to JSON compatible with saves.py
*/

(() => {
  // Utilities
  function now() { return performance.now(); }
  function timestampMs() { return Date.now(); }

  // Seeded RNG (Mulberry32)
  function createRng(seed) {
    let t = seed >>> 0;
    return function() {
      t += 0x6D2B79F5;
      let r = Math.imul(t ^ t >>> 15, 1 | t);
      r ^= r + Math.imul(r ^ r >>> 7, 61 | r);
      return ((r ^ r >>> 14) >>> 0) / 4294967296;
    }
  }

  // DOM
  const menu = document.getElementById('menu');
  const gameSection = document.getElementById('game');
  const endSection = document.getElementById('end');
  const startBtn = document.getElementById('start');
  const loadSample = document.getElementById('load-sample');
  const carSelect = document.getElementById('car-select');
  const seedInput = document.getElementById('seed');
  const screen = document.getElementById('screen');
  const ctx = screen.getContext('2d');
  const healthEl = document.getElementById('health');
  const igtEl = document.getElementById('igt');
  const seedDisplay = document.getElementById('seed-display');
  const pauseBtn = document.getElementById('pause');
  const exportBtn = document.getElementById('export');
  const restartBtn = document.getElementById('restart');
  const downloadEndBtn = document.getElementById('download-end');
  const endTitle = document.getElementById('end-title');
  const endSummary = document.getElementById('end-summary');

  const WIDTH = screen.width; const HEIGHT = screen.height;
  const TILE_W = 18; const TILE_H = 36; // tile cell size for visualizer
  const VISIBLE_ROWS = Math.floor(HEIGHT / TILE_H) + 4;

  // Game state
  let state = null;
  let lastTime = 0;
  let running = false;
  let rng = Math.random;
  let keys = {};

  function makeInitialState(seed, carModel) {
    const s = {
      seed: seed >>> 0,
      rngSeed: seed >>> 0,
      player: {
        x: 0, // lane offset
        lane: 0,
        speed: 0,
        angle: 0,
        health: 5,
        model: carModel,
      },
      igt: 0,
      playerpos: 0,
      tiles: [],
      tile_data: [],
      npcs: [],
      inventory: null,
      endpoint: null,
      success: false,
    };
    return s;
  }

  // Simple tile generator: produce rows of characters representing lanes
  function generateRow(rng, width = 11) {
    // width odd (center lane). '.' = road, 'S' = sidewalk, '#' crosswalk, '+' special
    const chars = [];
    for (let i = 0; i < width; i++) {
      const p = rng();
      if (i === 0 || i === width-1) {
        chars.push('S');
      } else {
        if (p < 0.02) chars.push('%'); // signal light
        else if (p < 0.08) chars.push('#');
        else if (p < 0.12) chars.push(',');
        else chars.push('.');
      }
    }
    return chars.join('');
  }

  function genInitialRows(s, count = VISIBLE_ROWS + 10) {
    s.tiles = [];
    s.tile_data = [];
    const localRng = createRng(s.rngSeed);
    for (let i = 0; i < count; i++) {
      const row = generateRow(localRng());
      s.tiles.push(row);
      // minimal tile_data format to keep compatibility
      s.tile_data.push({ layout: row, lanes: {} });
    }
  }

  // NPC representation: {x, y, speed, dir, lane}
  function spawnNpc(s, rng) {
    const lane = Math.floor(rng() * 5) + 3; // center lanes
    const dir = rng() < 0.5 ? 'down' : 'up';
    const speed = (rng() * 120) + (dir === 'down' ? 60 : -60);
    const x = WIDTH/2 + (lane - 6) * 40;
    const y = dir === 'down' ? HEIGHT + 40 : -40;
    s.npcs.push({ x, y, speed, dir, lane });
  }

  // Physics & update
  function gameStep(s, dt) {
    // dt seconds
    s.igt += dt;
    // spawn NPCs occasionally
    if (Math.random() < 0.02) {
      spawnNpc(s, rng);
    }

    // update NPCs
    for (let i = s.npcs.length - 1; i >= 0; i--) {
      const n = s.npcs[i];
      n.y += n.speed * dt;
      // remove offscreen
      if (n.y < -100 || n.y > HEIGHT + 100) s.npcs.splice(i, 1);
    }

    // player control
    const p = s.player;
    const accel = 300;
    if (keys['ArrowUp'] || keys['w']) { p.speed += accel * dt; }
    else { p.speed -= 120 * dt; }
    if (keys['ArrowDown'] || keys['s']) { p.speed -= accel * dt; }
    if (keys['ArrowLeft'] || keys['a']) { p.x -= 220 * dt; }
    if (keys['ArrowRight'] || keys['d']) { p.x += 220 * dt; }

    // clamp
    p.speed = Math.max(-120, Math.min(620, p.speed));
    p.x = Math.max(-WIDTH/2 + 40, Math.min(WIDTH/2 - 40, p.x));

    // collisions (simple bounding box vs npc)
    const playerRect = { x: WIDTH/2 + p.x - 20, y: HEIGHT - 220, w: 40, h: 70 };
    for (let i = s.npcs.length - 1; i >= 0; i--) {
      const n = s.npcs[i];
      const npcRect = { x: n.x - 20, y: n.y - 20, w: 40, h: 60 };
      if (rectsOverlap(playerRect, npcRect)) {
        // collision
        s.player.health -= 1;
        s.npcs.splice(i, 1);
        if (s.player.health <= 0) {
          s.player.health = 0;
          s.success = false;
          return { ended: true, reason: 'crash' };
        }
      }
    }

    // scroll world forward based on speed
    const travel = Math.max(0, p.speed) * dt;
    if (travel > TILE_H) {
      // advance rows proportionally
      const rows = Math.floor(travel / TILE_H);
      for (let r = 0; r < rows; r++) {
        const row = generateRow(rng());
        s.tiles.push(row);
        s.tile_data.push({ layout: row, lanes: {} });
        if (s.tiles.length > 5000) { s.tiles.shift(); s.tile_data.shift(); }
      }
    }

    // end condition (reach a long distance)
    s.playerpos += travel / TILE_H;
    if (s.playerpos > 800) {
      s.success = true;
      return { ended: true, reason: 'success' };
    }

    return { ended: false };
  }

  function rectsOverlap(a, b) {
    return !(a.x + a.w < b.x || b.x + b.w < a.x || a.y + a.h < b.y || b.y + b.h < a.y);
  }

  // Rendering
  function draw(s) {
    // clear
    ctx.fillStyle = '#77b0ff'; ctx.fillRect(0,0,WIDTH,HEIGHT);

    // draw rows bottom-up
    const rows = s.tiles.slice(-VISIBLE_ROWS - 2);
    const baseY = HEIGHT - 200;
    const perRow = TILE_H;

    for (let r = 0; r < rows.length; r++) {
      const row = rows[rows.length - 1 - r];
      const y = baseY - r * perRow;
      drawRow(row, y);
    }

    // draw NPCs
    for (const n of s.npcs) {
      ctx.fillStyle = '#ffcc00';
      ctx.fillRect(n.x - 18, n.y - 12, 36, 24);
    }

    // player
    const p = s.player;
    const px = WIDTH/2 + p.x;
    const py = HEIGHT - 220;
    ctx.save();
    ctx.translate(px, py);
    ctx.fillStyle = '#ff3333';
    ctx.fillRect(-22, -36, 44, 72);
    ctx.restore();

    // HUD
    healthEl.textContent = String(s.player.health);
    igtEl.textContent = s.igt.toFixed(1);
    seedDisplay.textContent = String(s.seed);
  }

  function drawRow(row, y) {
    const cols = row.length;
    const totalW = cols * TILE_W;
    const startX = (WIDTH - totalW) / 2;
    for (let c = 0; c < cols; c++) {
      const ch = row[c];
      const x = startX + c * TILE_W;
      if (ch === 'S') ctx.fillStyle = '#6bb96b';
      else if (ch === '.') ctx.fillStyle = '#303030';
      else if (ch === ',') ctx.fillStyle = '#404040';
      else if (ch === '#') ctx.fillStyle = '#aaaaaa';
      else if (ch === '%') ctx.fillStyle = '#ff6666';
      else ctx.fillStyle = '#2b2b2b';
      ctx.fillRect(x + 1, y - TILE_H + 2, TILE_W - 2, TILE_H - 4);
    }
  }

  // Export save JSON compatible with saves.save_run()
  function buildSave(s) {
    return {
      _magic: 'GTA6_SAVE_V1',
      seed: s.seed,
      igt: s.igt,
      health: s.player.health,
      car_model: s.player.model,
      success: s.success,
      tiles: s.tiles,
      tile_data: s.tile_data,
      endpoint: s.endpoint,
      saved_at: timestampMs(),
    };
  }

  function downloadJson(obj, filename) {
    const blob = new Blob([JSON.stringify(obj, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename; document.body.appendChild(a); a.click(); a.remove();
    URL.revokeObjectURL(url);
  }

  // Game loop
  function loop(t) {
    if (!running) return; // paused
    if (!lastTime) lastTime = t;
    const dtMs = t - lastTime; lastTime = t;
    const dt = dtMs / 1000;

    const res = gameStep(state, dt);
    draw(state);
    if (res.ended) {
      running = false;
      showEnd(res.reason);
    } else {
      requestAnimationFrame(loop);
    }
  }

  // UI control
  startBtn.addEventListener('click', () => {
    const seedVal = seedInput.value ? Number(seedInput.value) >>> 0 : Math.floor(Math.random() * 0xffffffff);
    const car = carSelect.value;
    rng = createRng(seedVal);
    state = makeInitialState(seedVal, car);
    genInitialRows(state, VISIBLE_ROWS + 30);
    state.player.health = 5;
    state.playerpos = 0;
    state.igt = 0;
    state.npcs = [];
    // show
    menu.classList.add('hidden');
    gameSection.classList.remove('hidden');
    endSection.classList.add('hidden');
    running = true; lastTime = 0;
    requestAnimationFrame(loop);
  });

  loadSample.addEventListener('click', () => {
    // create a short sample save
    const seedVal = 12345;
    const car = 'red_car';
    rng = createRng(seedVal);
    state = makeInitialState(seedVal, car);
    genInitialRows(state, VISIBLE_ROWS + 60);
    state.player.health = 4;
    menu.classList.add('hidden');
    gameSection.classList.remove('hidden');
    running = true; lastTime = 0; requestAnimationFrame(loop);
  });

  pauseBtn.addEventListener('click', () => {
    running = !running;
    if (running) { lastTime = 0; requestAnimationFrame(loop); pauseBtn.textContent = 'Pause'; }
    else pauseBtn.textContent = 'Resume';
  });

  exportBtn.addEventListener('click', () => {
    if (!state) return;
    const save = buildSave(state);
    const filename = `${save.seed}_${save.saved_at || timestampMs()}.json`;
    downloadJson(save, filename);
  });

  restartBtn.addEventListener('click', () => {
    gameSection.classList.add('hidden');
    endSection.classList.add('hidden');
    menu.classList.remove('hidden');
  });

  downloadEndBtn.addEventListener('click', () => {
    if (!state) return;
    const save = buildSave(state);
    const filename = `${save.seed}_${save.saved_at || timestampMs()}.json`;
    downloadJson(save, filename);
  });

  function showEnd(reason) {
    gameSection.classList.add('hidden');
    endSection.classList.remove('hidden');
    endTitle.textContent = reason === 'success' ? 'You made it!' : 'Game over';
    endSummary.textContent = `Result: ${reason} — igt ${state.igt.toFixed(1)}s — health ${state.player.health}`;
  }

  // keyboard
  window.addEventListener('keydown', (ev) => { keys[ev.key] = true; });
  window.addEventListener('keyup', (ev) => { keys[ev.key] = false; });

  // initial
  function init() {
    // center menu
  }
  init();
})();
