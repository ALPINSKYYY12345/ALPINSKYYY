from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path
from datetime import date

app = Flask(__name__)
DB = Path(__file__).with_name('database.db')

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute('''CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL,
            jenis TEXT NOT NULL CHECK(jenis IN ('pemasukan','pengeluaran')),
            kategori TEXT NOT NULL,
            keterangan TEXT NOT NULL,
            jumlah INTEGER NOT NULL CHECK(jumlah > 0)
        )''')

@app.route('/')
def index():
    return render_template('index.html')

@app.get('/api/transaksi')
def get_transaksi():
    # Ambil parameter query dari URL (contoh: /api/transaksi?bulan=10&tahun=2026 atau ?jenis=pengeluaran)
    bulan = request.args.get('bulan')  # format angka string: "01", "02", ..., "12"
    tahun = request.args.get('tahun')  # format angka string: "2026"
    jenis = request.args.get('jenis')  # "pemasukan" atau "pengeluaran"

    query = 'SELECT * FROM transaksi WHERE 1=1'
    params = []

    # Filter jenis transaksi jika dikirim
    if jenis and jenis != 'semua':
        query += ' AND jenis = ?'
        params.append(jenis)

    # Filter tahun jika dikirim (menggunakan strftime SQLite)
    if tahun and tahun != 'semua':
        query += " AND strftime('%Y', tanggal) = ?"
        params.append(tahun)

    # Filter bulan jika dikirim
    if bulan and bulan != 'semua':
        # Memastikan format bulan 2 digit (misal: '9' jadi '09')
        bulan_formatted = f"{int(bulan):02d}"
        query += " AND strftime('%m', tanggal) = ?"
        params.append(bulan_formatted)

    query += ' ORDER BY tanggal DESC, id DESC'

    with connect() as con:
        rows = con.execute(query, params).fetchall()
    return jsonify([dict(r) for r in rows])

@app.post('/api/transaksi')
def tambah_transaksi():
    data = request.get_json(silent=True) or {}
    try:
        jenis = data['jenis']
        kategori = str(data['kategori']).strip()
        keterangan = str(data['keterangan']).strip()
        tanggal = date.fromisoformat(data['tanggal']).isoformat()
        jumlah = int(data['jumlah'])
        if jenis not in ('pemasukan', 'pengeluaran') or not kategori or not keterangan or jumlah <= 0:
            raise ValueError('Data tidak valid')
    except (KeyError, TypeError, ValueError):
        return jsonify(error='Periksa kembali data transaksi.'), 400
    with connect() as con:
        cur = con.execute('INSERT INTO transaksi (tanggal, jenis, kategori, keterangan, jumlah) VALUES (?, ?, ?, ?, ?)',
                          (tanggal, jenis, kategori, keterangan, jumlah))
        new_id = cur.lastrowid
    return jsonify(id=new_id, message='Transaksi berhasil disimpan.'), 201

@app.delete('/api/transaksi/<int:id>')
def hapus_transaksi(id):
    with connect() as con:
        cur = con.execute('DELETE FROM transaksi WHERE id = ?', (id,))
        if cur.rowcount == 0:
            return jsonify(error='Transaksi tidak ditemukan.'), 404
    return jsonify(message='Transaksi dihapus.')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)