import matplotlib
# 必須加上這行，設定 matplotlib 在背景執行，避免在 Flask 執行時跳出視窗導致執行緒當機
matplotlib.use('Agg') 

from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # 1. 檢查檔案是否存在
        if 'csv_file' not in request.files:
            return jsonify({'status': 'error', 'message': '未上傳 CSV 檔案'})
        
        file = request.files['csv_file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': '檔案名稱為空'})

        # 2. 讀取與整理 CSV
        # 依照您的檔案格式：跳過前2列，並以分號 ";" 作為分隔符號
        df = pd.read_csv(file, sep=";", skiprows=2)
        
        # 清除因為每一列最後一個分號而產生的全空欄位
        df = df.dropna(axis=1, how='all')
        
        # 清除欄位名稱前後可能多餘的空白
        df.columns = [col.strip() for col in df.columns]

        # 防呆檢查：確保檔案至少有4個欄位
        if len(df.columns) < 4:
            return jsonify({'status': 'error', 'message': 'CSV 欄位數量不足，請確認是否為正確的 S-parameter 檔案'})

        # 取得欄位名稱
        time_col = df.columns[0]
        sdd11_col = df.columns[1]
        sdd22_col = df.columns[2]
        sdd21_col = df.columns[3]

        # 3. 使用 Python (Matplotlib) 繪製波形圖表
        fig, axes = plt.subplots(3, 1, figsize=(10, 12))

        # 圖表 1：Trc1_Z<-Sdd11
        axes[0].plot(df[time_col], df[sdd11_col], color='#1f77b4')
        axes[0].set_title(f"{sdd11_col} vs Time")
        axes[0].set_xlabel("Time (s)")
        axes[0].set_ylabel("Sdd11 (Ohm)")
        axes[0].grid(True, linestyle='--', alpha=0.6)

        # 圖表 2：Trc2_Z<-Sdd22
        axes[1].plot(df[time_col], df[sdd22_col], color='#d62728')
        axes[1].set_title(f"{sdd22_col} vs Time")
        axes[1].set_xlabel("Time (s)")
        axes[1].set_ylabel("Sdd22 (Ohm)")
        axes[1].grid(True, linestyle='--', alpha=0.6)

        # 圖表 3：Trc3_Sdd21
        axes[2].plot(df[time_col], df[sdd21_col], color='#2ca02c')
        axes[2].set_title(f"{sdd21_col} vs Time")
        axes[2].set_xlabel("Time (s)")
        axes[2].set_ylabel("Sdd21 (dB)")
        axes[2].grid(True, linestyle='--', alpha=0.6)

        plt.tight_layout()

        # 4. 將圖表轉換為 Base64 字串
        img_io = io.BytesIO()
        plt.savefig(img_io, format='png', dpi=120, bbox_inches='tight')  
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        plt.close(fig)

        # 5. 回傳給前端
        return jsonify({
            'status': 'success',
            'message': '圖表繪製完成！',
            'chart_image': 'data:image/png;base64,' + img_base64
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'分析失敗: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
