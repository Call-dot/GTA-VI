// Lightweight tile-string preview. Renders the tile layout as coloured cells and animates vertical scroll.
(function(){
  const el = document.getElementById('save-data')
  if(!el) return
  const record = JSON.parse(el.textContent)
  const tiles = record.tiles || []
  const canvas = document.getElementById('preview')
  const ctx = canvas.getContext('2d')

  // simple char -> colour map (grass vs road vs sidewalk)
  const map = {
    '.': '#3b3b3b', // road
    ',': '#3b3b3b',
    '+': '#3b3b3b',
    '$': '#3b3b3b',
    'S': '#7cae6b', // sidewalk/green
    '_': '#76a6ff', // water/sky placeholder
    '|': '#606060',
    '/': '#666633',
    ':': '#6b6b6b'
  }

  const cellW = 18
  const cellH = 18
  canvas.width = 20 * cellW
  canvas.height = 30 * cellH

  let offset = 0
  function draw(){
    ctx.fillStyle = '#0f1720'
    ctx.fillRect(0,0,canvas.width,canvas.height)

    // draw rows from tiles list; bottom-aligned so playerpos looks like forward motion
    for(let r=0; r<tiles.length; r++){
      const row = tiles[r]
      for(let c=0;c<row.length;c++){
        const ch = row[c]
        const color = map[ch] || '#2b2b2b'
        const x = c * cellW + (canvas.width - row.length*cellW)/2
        const y = (r * cellH) - offset
        // only draw if visible
        if(y > -cellH && y < canvas.height){
          ctx.fillStyle = color
          ctx.fillRect(x, y, cellW-1, cellH-1)
        }
      }
    }

    offset += 1.2
    if(offset > cellH) offset = 0
    requestAnimationFrame(draw)
  }
  requestAnimationFrame(draw)
})()
