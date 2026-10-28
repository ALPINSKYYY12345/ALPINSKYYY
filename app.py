from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Data sementara disimpan di memori (list of dictionaries)
transactions = [
    {"id": 1, "tipe": "pemasukan", "kategori": "Uang Saku", "jumlah": 2000000, "catatan": "Transfer Orang Tua"},
    {"id": 2, "tipe": "pengeluaran", "kategori": "Makanan", "jumlah": 50000, "catatan": "Makan Siang"}
]

@app.route('/')
def index():
    # Hitung ringkasan saldo langsung di kode Python
    total_pemasukan = sum(t['jumlah'] for t in transactions if t['tipe'] == 'pemasukan')
    total_pengeluaran = sum(t['jumlah'] for t in transactions if t['tipe'] == 'pengeluaran')
    total_saldo = total_pemasukan - total_pengeluaran

    return render_template('index.html', 
                           transactions=transactions, 
                           total_saldo=total_saldo, 
                           total_pemasukan=total_pemasukan, 
                           total_pengeluaran=total_pengeluaran)

@app.route('/tambah', methods=['POST'])
def tambah_transaksi():
    # Mengambil data dari form dan menambahkan ke list
    tipe = request.form.get('tipe')
    kategori = request.form.get('kategori')
    jumlah = int(request.form.get('jumlah', 0))
    catatan = request.form.get('catatan')

    new_id = len(transactions) + 1
    transactions.append({
        "id": new_id,
        "tipe": tipe,
        "kategori": kategori,
        "jumlah": jumlah,
        "catatan": catatan
    })
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
