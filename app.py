from flask import Flask, render_template, request, jsonify
import pandas as pd
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'csv_file' not in request.files:
            return jsonify({'status': 'error', 'message': '未上傳 CSV 檔案'})
        
        file = request.files['csv_file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': '檔案名稱為空'})

        # 讀取 CSV
        df = pd.read_csv(file)
        cols = df.columns.tolist()

        if 'FreqGHz' not in cols:
            return jsonify({'status': 'error', 'message': 'CSV 缺少 FreqGHz 欄位'})

        sim_col = 'SimdB' if 'SimdB' in cols else 'SimValue' if 'SimValue' in cols else None
        spec_col = 'SpecdB' if 'SpecdB' in cols else 'Spec_Value' if 'Spec_Value' in cols else None

        if not sim_col or not spec_col:
            return jsonify({'status': 'error', 'message': 'CSV 缺少 Sim/Spec 相關欄位'})

        # 數據分析
        max_val = df[sim_col].max()
        min_val = df[sim_col].min()

        # Pass/Fail 判斷 (可依需求調整邏輯)
        df['Pass'] = df[sim_col] <= df[spec_col]
        is_pass = bool(df['Pass'].all())

        return jsonify({
            'status': 'success',
            'message': '分析完成！',
            'data': {
                'freq': df['FreqGHz'].tolist(),
                'sim': df[sim_col].tolist(),
                'spec': df[spec_col].tolist(),
                'sim_name': sim_col,
                'spec_name': spec_col,
                'max': float(max_val),
                'min': float(min_val),
                'is_pass': is_pass
            }
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)