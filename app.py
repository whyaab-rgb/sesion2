<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>BSJP Screener - Single Table</title>
  <style>
    :root {
      --bg: #08111f;
      --panel: #0d1b2a;
      --panel-2: #10253a;
      --line: #1f3c58;
      --text: #e8f1ff;
      --muted: #9eb2cb;
      --green: #16c784;
      --red: #ff5b6e;
      --yellow: #f5b700;
      --blue: #2d8cff;
      --purple: #8b5cf6;
      --orange: #ff8f3d;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, Arial, Helvetica, sans-serif;
      background: linear-gradient(180deg, #07101c 0%, #0a1625 100%);
      color: var(--text);
    }

    .wrap {
      max-width: 1800px;
      margin: 0 auto;
      padding: 18px;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 14px;
    }

    .title-box h1 {
      margin: 0;
      font-size: 24px;
      letter-spacing: 0.3px;
    }

    .title-box p {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 13px;
    }

    .controls {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
      background: rgba(255,255,255,0.03);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px;
    }

    .control {
      display: flex;
      flex-direction: column;
      gap: 6px;
      min-width: 140px;
    }

    .control label {
      font-size: 12px;
      color: var(--muted);
    }

    input, select, button {
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--text);
      border-radius: 10px;
      padding: 10px 12px;
      outline: none;
    }

    input:focus, select:focus {
      border-color: var(--blue);
    }

    button {
      cursor: pointer;
      font-weight: 600;
      background: linear-gradient(180deg, #15304d 0%, #10253a 100%);
    }

    button:hover {
      filter: brightness(1.08);
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(5, minmax(140px, 1fr));
      gap: 12px;
      margin: 12px 0 16px;
    }

    .card {
      background: linear-gradient(180deg, rgba(16,37,58,.9), rgba(10,22,37,.96));
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px 14px;
      box-shadow: 0 8px 24px rgba(0,0,0,.2);
    }

    .card .k {
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
    }

    .card .v {
      font-size: 24px;
      font-weight: 700;
    }

    .table-wrap {
      border: 1px solid var(--line);
      border-radius: 16px;
      overflow: hidden;
      background: var(--panel);
      box-shadow: 0 12px 30px rgba(0,0,0,.24);
    }

    .table-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      background: #0a1b2d;
      color: var(--muted);
      font-size: 13px;
      flex-wrap: wrap;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 1500px;
    }

    thead th {
      position: sticky;
      top: 0;
      z-index: 2;
      background: #14355a;
      color: #eef6ff;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .3px;
      padding: 10px 8px;
      border-bottom: 1px solid var(--line);
      white-space: nowrap;
      cursor: pointer;
    }

    tbody td {
      padding: 8px;
      border-bottom: 1px solid rgba(255,255,255,.05);
      font-size: 13px;
      white-space: nowrap;
      text-align: center;
    }

    tbody tr:nth-child(odd) { background: rgba(255,255,255,.015); }
    tbody tr:hover { background: rgba(45,140,255,.08); }

    .left { text-align: left; }
    .ticker {
      font-weight: 700;
      color: #d7e8ff;
    }

    .gain-up, .up { color: var(--green); font-weight: 700; }
    .gain-down, .down { color: var(--red); font-weight: 700; }
    .neutral { color: #d9e6f5; }

    .badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 11px;
      font-weight: 700;
      min-width: 80px;
    }

    .b-blue { background: rgba(45,140,255,.16); color: #91c0ff; border: 1px solid rgba(45,140,255,.25); }
    .b-green { background: rgba(22,199,132,.16); color: #8ef1c9; border: 1px solid rgba(22,199,132,.25); }
    .b-red { background: rgba(255,91,110,.16); color: #ffb2bc; border: 1px solid rgba(255,91,110,.25); }
    .b-yellow { background: rgba(245,183,0,.16); color: #ffd978; border: 1px solid rgba(245,183,0,.25); }
    .b-purple { background: rgba(139,92,246,.16); color: #c9b0ff; border: 1px solid rgba(139,92,246,.25); }
    .b-orange { background: rgba(255,143,61,.16); color: #ffc18e; border: 1px solid rgba(255,143,61,.25); }
    .b-gray { background: rgba(255,255,255,.08); color: #d4dfec; border: 1px solid rgba(255,255,255,.1); }

    .footer-note {
      margin-top: 12px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
    }

    .mono { font-variant-numeric: tabular-nums; }
    .scroll-x { overflow: auto; }

    @media (max-width: 980px) {
      .stats { grid-template-columns: repeat(2, minmax(140px, 1fr)); }
      .title-box h1 { font-size: 20px; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <div class="title-box">
        <h1>BSJP Screener - Single Table</h1>
        <p>1 tabel, lebih banyak emiten, filter harga maksimal 1000, auto refresh 60 detik, dan search emiten.</p>
      </div>

      <div class="controls">
        <div class="control">
          <label for="search">Search Emiten</label>
          <input id="search" type="text" placeholder="Contoh: BBRI, TLKM, BRIS" />
        </div>

        <div class="control">
          <label for="priceCap">Batas Harga Maks</label>
          <input id="priceCap" type="number" min="1" value="1000" />
        </div>

        <div class="control">
          <label for="rows">Jumlah Baris</label>
          <select id="rows">
            <option value="25">25</option>
            <option value="50" selected>50</option>
            <option value="75">75</option>
            <option value="100">100</option>
          </select>
        </div>

        <div class="control">
          <label for="sortBy">Urutkan</label>
          <select id="sortBy">
            <option value="gain1">Gain 1</option>
            <option value="rvol">RVOL</option>
            <option value="now">Harga Now</option>
            <option value="rsi5m">RSI 5M</option>
            <option value="value">Value</option>
          </select>
        </div>

        <div class="control">
          <label for="refreshInfo">Refresh</label>
          <button id="refreshBtn">Refresh Sekarang</button>
        </div>
      </div>
    </div>

    <div class="stats">
      <div class="card"><div class="k">Jumlah Emiten Tampil</div><div class="v" id="statCount">0</div></div>
      <div class="card"><div class="k">Harga Maks Aktif</div><div class="v" id="statCap">1000</div></div>
      <div class="card"><div class="k">Bull Trend</div><div class="v" id="statBull">0</div></div>
      <div class="card"><div class="k">Bear Trend</div><div class="v" id="statBear">0</div></div>
      <div class="card"><div class="k">Refresh Berikutnya</div><div class="v" id="statRefresh">60s</div></div>
    </div>

    <div class="table-wrap">
      <div class="table-top">
        <div>Mode: <strong>Single Table</strong></div>
        <div>Auto refresh setiap <strong>60 detik</strong></div>
        <div>Last update: <strong id="lastUpdate">-</strong></div>
      </div>

      <div class="scroll-x">
        <table id="screenerTable">
          <thead>
            <tr>
              <th data-sort="ticker">Emiten</th>
              <th data-sort="gain1">Gain 1</th>
              <th data-sort="wick">Wick</th>
              <th data-sort="action">Aksi</th>
              <th data-sort="signal">Sinyal</th>
              <th data-sort="rvol">RVOL</th>
              <th data-sort="entry">Entry</th>
              <th data-sort="now">Now</th>
              <th data-sort="tp">TP</th>
              <th data-sort="sl">SL</th>
              <th data-sort="profit">Profit</th>
              <th data-sort="toTp">% To TP</th>
              <th data-sort="rsiSig">RSI Sig</th>
              <th data-sort="rsi5m">RSI 5M</th>
              <th data-sort="value">Val</th>
              <th data-sort="phase">Fase</th>
              <th data-sort="trend">Trend</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>

    <div class="footer-note">
      Catatan: file ini sudah siap untuk tampilan screener. Saat ini data memakai generator demo agar UI langsung jalan. Untuk real-time BSJP/TradingView/RTI/IDX, ganti fungsi <span class="mono">fetchMarketData()</span> ke API atau webhook data Anda. Filter default hanya menampilkan emiten dengan harga <strong>≤ 1000</strong>.
    </div>
  </div>

  <script>
    const STOCK_POOL = [
      'AADI','ADHI','AKRA','ASBI','ASII','ASSA','BBKP','BBRI','BBYB','BIPI','BJTM','BMRI','BOGA','BRIS','BRMS','BTPS',
      'BUKA','BUMI','CMRY','CPIN','DOID','ELSA','ENRG','ERAA','ESSA','EXCL','FILM','GOTO','HEAL','HRUM','INCO','INDY',
      'ISAT','ITMG','JSMR','JPFA','KAEF','KIJA','KLBF','LPKR','LSIP','MAIN','MAPA','MDKA','MEDC','MIDI','MTEL','MYOR',
      'PGAS','PNLF','PTBA','PTPP','PWON','RAJA','SCMA','SIDO','SMGR','SMRA','SRTG','SSIA','TBIG','TLKM','TOWR','TPIA',
      'UNTR','UNVR','WIKA','WSKT','ZINC','AMMN','BRPT','TINS','ANTM','BKSL','CLEO','DMAS','HOKI','ICBP','IMPC','IPTV',
      'ITMG','JKON','MAPI','MARK','NCKL','PNBN','PPRE','PTRO','SAME','SILO','SMDR','TAPG','TKIM','TMAS','TOBA','UCID'
    ];

    let sortState = { key: 'gain1', dir: 'desc' };
    let countdown = 60;
    let autoRefreshTimer = null;
    let countdownTimer = null;
    let currentData = [];

    const tbody = document.querySelector('#screenerTable tbody');
    const searchEl = document.getElementById('search');
    const priceCapEl = document.getElementById('priceCap');
    const rowsEl = document.getElementById('rows');
    const sortByEl = document.getElementById('sortBy');
    const refreshBtn = document.getElementById('refreshBtn');

    function rand(min, max, decimals = 0) {
      const n = Math.random() * (max - min) + min;
      return Number(n.toFixed(decimals));
    }

    function pick(arr) {
      return arr[Math.floor(Math.random() * arr.length)];
    }

    function formatPct(v) {
      return `${v > 0 ? '' : ''}${v.toFixed(1)}%`;
    }

    function formatMoney(v) {
      if (v >= 1_000_000_000) return (v / 1_000_000_000).toFixed(1) + 'B';
      if (v >= 1_000_000) return (v / 1_000_000).toFixed(1) + 'M';
      return v.toLocaleString('id-ID');
    }

    function actionBadge(action) {
      const map = {
        'AT ENTRY': 'b-blue',
        'WATCH GC': 'b-gray',
        'HOLD': 'b-purple',
        'SIAP BELI': 'b-green',
        'LATE': 'b-orange'
      };
      return `<span class="badge ${map[action] || 'b-gray'}">${action}</span>`;
    }

    function signalBadge(signal) {
      const map = {
        'ON TRACK': 'b-green',
        'DIST': 'b-red',
        'REBOUND': 'b-orange',
        'AKUM': 'b-blue',
        'WAIT': 'b-gray',
        'SUPER': 'b-purple',
        'HAKA': 'b-yellow'
      };
      return `<span class="badge ${map[signal] || 'b-gray'}">${signal}</span>`;
    }

    function phaseBadge(phase) {
      const map = {
        'AKUM': 'b-purple',
        'BIG AKUM': 'b-purple',
        'NETRAL': 'b-gray',
        'BIG DIST': 'b-red'
      };
      return `<span class="badge ${map[phase] || 'b-gray'}">${phase}</span>`;
    }

    function trendBadge(trend) {
      return `<span class="badge ${trend === 'BULL' ? 'b-green' : 'b-red'}">${trend}</span>`;
    }

    async function fetchMarketData() {
      const API_URL = 'https://api-anda.com/bsjp'; // ganti ke endpoint API Anda
      const API_HEADERS = {
        'Content-Type': 'application/json'
        // 'Authorization': 'Bearer TOKEN_ANDA',
        // 'x-api-key': 'API_KEY_ANDA'
      };

      const res = await fetch(API_URL, {
        method: 'GET',
        headers: API_HEADERS,
        cache: 'no-store'
      });

      if (!res.ok) {
        throw new Error(`Gagal fetch API: ${res.status} ${res.statusText}`);
      }

      const json = await res.json();
      const sourceRows = Array.isArray(json)
        ? json
        : Array.isArray(json.data)
          ? json.data
          : Array.isArray(json.results)
            ? json.results
            : Array.isArray(json.items)
              ? json.items
              : [];

      return sourceRows.map(item => {
        const now = Number(
          item.now ?? item.price ?? item.harga ?? item.last ?? item.close ?? 0
        );
        const entry = Number(item.entry ?? item.buy_price ?? item.entryPrice ?? now);
        const tp = Number(item.tp ?? item.take_profit ?? item.target ?? Math.round(now * 1.04));
        const sl = Number(item.sl ?? item.stop_loss ?? item.cutloss ?? Math.round(now * 0.96));
        const gain1 = Number(item.gain1 ?? item.gain ?? item.change_pct ?? item.changePercent ?? 0);
        const wick = Number(item.wick ?? item.upper_wick ?? item.wick_pct ?? 0);
        const rvol = Number(item.rvol ?? item.relative_volume ?? item.rvol_pct ?? 0);
        const profit = Number(item.profit ?? (((now - entry) / (entry || 1)) * 100));
        const toTp = Number(item.toTp ?? item.to_tp ?? item.percent_to_tp ?? (((tp - now) / (now || 1)) * 100));
        const rsi5m = Number(item.rsi5m ?? item.rsi_5m ?? item.rsi ?? 0);

        const action = String(item.action ?? item.aksi ?? item.recommendation ?? 'WATCH GC').toUpperCase();
        const signal = String(item.signal ?? item.sinyal ?? item.status ?? 'WAIT').toUpperCase();
        const rsiSig = String(item.rsiSig ?? item.rsi_signal ?? (rsi5m >= 50 ? 'UP' : 'DEAD')).toUpperCase();
        const phase = String(item.phase ?? item.fase ?? item.market_phase ?? 'NETRAL').toUpperCase();
        const trend = String(item.trend ?? item.direction ?? (gain1 >= 0 ? 'BULL' : 'BEAR')).toUpperCase();

        return {
          ticker: String(item.ticker ?? item.symbol ?? item.kode ?? item.emiten ?? '').toUpperCase(),
          gain1,
          wick,
          action,
          signal,
          rvol,
          entry,
          now,
          tp,
          sl,
          profit,
          toTp,
          rsiSig,
          rsi5m,
          value: Number(item.value ?? item.val ?? item.volume_value ?? item.turnover ?? 0),
          phase,
          trend
        };
      }).filter(item => item.ticker && Number.isFinite(item.now));
    }

    function getFilteredSortedData(data) {
      const q = searchEl.value.trim().toUpperCase();
      const cap = Number(priceCapEl.value || 1000);
      const rows = Number(rowsEl.value || 50);

      let result = data.filter(item => item.now <= cap);

      if (q) {
        result = result.filter(item => item.ticker.includes(q));
      }

      result.sort((a, b) => {
        const key = sortState.key;
        const va = a[key];
        const vb = b[key];
        if (typeof va === 'string' && typeof vb === 'string') {
          return sortState.dir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
        }
        return sortState.dir === 'asc' ? va - vb : vb - va;
      });

      return result.slice(0, rows);
    }

    function renderTable() {
      const rows = getFilteredSortedData(currentData);

      tbody.innerHTML = rows.map(item => `
        <tr>
          <td class="left ticker">${item.ticker}</td>
          <td class="${item.gain1 >= 0 ? 'gain-up' : 'gain-down'} mono">${formatPct(item.gain1)}</td>
          <td class="neutral mono">${formatPct(item.wick)}</td>
          <td>${actionBadge(item.action)}</td>
          <td>${signalBadge(item.signal)}</td>
          <td class="mono">${item.rvol}%</td>
          <td class="mono">${item.entry}</td>
          <td class="mono">${item.now}</td>
          <td class="mono up">${item.tp}</td>
          <td class="mono down">${item.sl}</td>
          <td class="mono ${item.profit >= 0 ? 'up' : 'down'}">${formatPct(item.profit)}</td>
          <td class="mono ${item.toTp >= 3 ? 'up' : 'neutral'}">${formatPct(item.toTp)}</td>
          <td class="${item.rsiSig === 'UP' ? 'up' : 'down'}">${item.rsiSig}</td>
          <td class="mono">${item.rsi5m}</td>
          <td class="mono">${formatMoney(item.value)}</td>
          <td>${phaseBadge(item.phase)}</td>
          <td>${trendBadge(item.trend)}</td>
        </tr>
      `).join('');

      updateStats(rows);
    }

    function updateStats(rows) {
      document.getElementById('statCount').textContent = rows.length;
      document.getElementById('statCap').textContent = Number(priceCapEl.value || 1000).toLocaleString('id-ID');
      document.getElementById('statBull').textContent = rows.filter(r => r.trend === 'BULL').length;
      document.getElementById('statBear').textContent = rows.filter(r => r.trend === 'BEAR').length;
    }

    async function refreshData() {
      currentData = await fetchMarketData();
      renderTable();
      document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString('id-ID');
      countdown = 60;
      document.getElementById('statRefresh').textContent = `${countdown}s`;
    }

    function startAutoRefresh() {
      clearInterval(autoRefreshTimer);
      clearInterval(countdownTimer);

      autoRefreshTimer = setInterval(async () => {
        await refreshData();
      }, 60000);

      countdownTimer = setInterval(() => {
        countdown -= 1;
        if (countdown < 0) countdown = 60;
        document.getElementById('statRefresh').textContent = `${countdown}s`;
      }, 1000);
    }

    document.querySelectorAll('th[data-sort]').forEach(th => {
      th.addEventListener('click', () => {
        const key = th.dataset.sort;
        if (sortState.key === key) {
          sortState.dir = sortState.dir === 'asc' ? 'desc' : 'asc';
        } else {
          sortState.key = key;
          sortState.dir = 'desc';
        }
        sortByEl.value = key;
        renderTable();
      });
    });

    searchEl.addEventListener('input', renderTable);
    priceCapEl.addEventListener('input', renderTable);
    rowsEl.addEventListener('change', renderTable);
    sortByEl.addEventListener('change', (e) => {
      sortState.key = e.target.value;
      sortState.dir = 'desc';
      renderTable();
    });
    refreshBtn.addEventListener('click', refreshData);

    (async function init() {
      try {
        await refreshData();
        startAutoRefresh();
      } catch (err) {
        console.error(err);
        document.getElementById('lastUpdate').textContent = 'API error';
        tbody.innerHTML = `
          <tr>
            <td colspan="17" style="text-align:left;padding:16px;color:#ffb2bc;">
              Gagal mengambil data API. Periksa URL endpoint, header auth, CORS, dan format response API Anda.
            </td>
          </tr>
        `;
      }
    })();
  </script>
</body>
</html>
